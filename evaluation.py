"""
CyberIncident AI - Evaluation Module
Evaluates the existing NER + RAG pipeline without changing the backend.

Metrics:
- Entity detection Precision / Recall / F1
- Attack-type classification accuracy
- Precision@3
- Recall@3
- MRR
- Average pipeline latency
- Context grounding rate (basic guardrail)

Run:
    python evaluation.py

Or import:
    from evaluation import run_evaluation
    results = run_evaluation()
"""

from pathlib import Path
import sys
import re
import time
import json

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rag import build_rag_context


# ============================================================
# EVALUATION DATASET
# ============================================================

TEST_CASES = [
    {
        "id": "EVAL-01",
        "text": (
            "Employee Sarah Mathews at NovaGrid Technologies reported "
            "an account takeover attempt. Multiple failed login attempts "
            "from IP address 185.72.44.19 were followed by a successful "
            "login to the cloud server from Bucharest, Romania. "
            "Confidential project files were downloaded. The incident "
            "was classified as HIGH severity."
        ),
        "person": "Sarah Mathews",
        "organization": "NovaGrid Technologies",
        "location": "Bucharest, Romania",
        "attack_type": "Account Takeover",
        "keywords": [
            "account",
            "login",
            "authentication",
            "cloud",
            "unauthorized"
        ],
    },
    {
        "id": "EVAL-02",
        "text": (
            "The security team detected repeated failed authentication "
            "attempts against the VPN server from IP address 185.199.110.25. "
            "After many failed attempts, one login succeeded. The event "
            "was classified as HIGH severity."
        ),
        "person": None,
        "organization": None,
        "location": None,
        "attack_type": "Brute Force Attack",
        "keywords": [
            "brute force",
            "failed login",
            "authentication",
            "password",
            "credential"
        ],
    },
    {
        "id": "EVAL-03",
        "text": (
            "An employee at Orion Systems received a phishing email from "
            "an unknown sender. The message contained a fake Microsoft "
            "login page and attempted to collect the employee's credentials. "
            "The incident was classified as HIGH severity."
        ),
        "person": None,
        "organization": "Orion Systems",
        "location": None,
        "attack_type": "Phishing Attack",
        "keywords": [
            "phishing",
            "email",
            "credential",
            "fake login",
            "social engineering"
        ],
    },
    {
        "id": "EVAL-04",
        "text": (
            "A ransomware attack was detected on the file server of "
            "BluePeak Technologies. Several project documents were "
            "encrypted and a ransom note appeared on affected systems. "
            "The incident was classified as CRITICAL severity."
        ),
        "person": None,
        "organization": "BluePeak Technologies",
        "location": None,
        "attack_type": "Ransomware Attack",
        "keywords": [
            "ransomware",
            "encryption",
            "encrypted",
            "file server",
            "ransom"
        ],
    },
    {
        "id": "EVAL-05",
        "text": (
            "A SQL injection attack was detected against the web application "
            "of DataCore Solutions. Suspicious database queries were observed "
            "and unauthorized database access was suspected. The incident "
            "was classified as HIGH severity."
        ),
        "person": None,
        "organization": "DataCore Solutions",
        "location": None,
        "attack_type": "SQL Injection",
        "keywords": [
            "sql injection",
            "database",
            "query",
            "web application",
            "unauthorized access"
        ],
    },
]


# ============================================================
# HELPERS
# ============================================================

def normalize(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip().lower())


def values_from_entities(entities, *keys):
    values = []

    if not isinstance(entities, dict):
        return values

    for key in keys:
        data = entities.get(key, [])

        if isinstance(data, str):
            data = [data]

        if isinstance(data, (list, tuple)):
            for item in data:
                item = str(item).strip()
                if item and normalize(item) not in [
                    normalize(x) for x in values
                ]:
                    values.append(item)

    return values


def contains_expected(expected, values):
    if not expected:
        return None

    target = normalize(expected)

    for value in values:
        candidate = normalize(value)
        if target == candidate or target in candidate or candidate in target:
            return True

    return False


def normalize_attack(value):
    text = normalize(value)

    mappings = {
        "brute force": "brute force attack",
        "brute-force": "brute force attack",
        "brute force attack": "brute force attack",
        "phishing": "phishing attack",
        "phishing attack": "phishing attack",
        "ransomware": "ransomware attack",
        "ransomware attack": "ransomware attack",
        "sql injection": "sql injection",
        "account takeover": "account takeover",
    }

    return mappings.get(text, text)


def get_retrieved_items(result):
    items = []

    if not isinstance(result, dict):
        return items

    for key in (
        "retrieved_knowledge",
        "retrieved_context",
        "retrieved_documents",
        "documents",
        "knowledge",
    ):
        data = result.get(key)

        if data:
            if isinstance(data, list):
                return data
            if isinstance(data, str):
                return [data]

    return items


def item_text(item):
    if isinstance(item, str):
        return item

    if isinstance(item, dict):
        parts = []

        for key in (
            "title",
            "source",
            "text",
            "content",
            "chunk",
            "document",
        ):
            value = item.get(key)
            if value:
                parts.append(str(value))

        return " ".join(parts)

    return str(item)


def relevance_score(item, keywords):
    text = normalize(item_text(item))

    if not text:
        return 0

    return sum(
        1 for keyword in keywords
        if normalize(keyword) in text
    )


def entity_metrics(case_results):
    tp = fp = fn = 0

    for result in case_results:
        expected = result["expected_entities"]
        actual = result["actual_entities"]

        for entity_type in (
            "PERSON",
            "ORGANIZATION",
            "LOCATION",
        ):
            exp = expected.get(entity_type)
            act = actual.get(entity_type, [])

            if exp:
                if contains_expected(exp, act):
                    tp += 1
                else:
                    fn += 1

                # Extra detected entities count as false positives
                if len(act) > 1:
                    fp += len(act) - 1

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0
    )

    return precision, recall, f1


# ============================================================
# MAIN EVALUATION
# ============================================================

def run_evaluation(verbose=True):

    results = []

    attack_correct = 0
    p_at_3_values = []
    recall_at_3_values = []
    reciprocal_ranks = []
    latencies = []
    grounding_values = []

    for case in TEST_CASES:

        start = time.perf_counter()

        try:
            rag_result = build_rag_context(case["text"])

            elapsed = time.perf_counter() - start
            latencies.append(elapsed)

            entities = (
                rag_result.get("entities", {})
                if isinstance(rag_result, dict)
                else {}
            )

            actual_entities = {
                "PERSON": values_from_entities(
                    entities,
                    "PERSON",
                    "person"
                ),
                "ORGANIZATION": values_from_entities(
                    entities,
                    "ORGANIZATION",
                    "ORG",
                    "organization"
                ),
                "LOCATION": values_from_entities(
                    entities,
                    "LOCATION",
                    "GPE",
                    "location"
                ),
            }

            actual_attack = ""

            if isinstance(entities, dict):
                attack_values = values_from_entities(
                    entities,
                    "ATTACK_TYPE",
                    "attack_type"
                )

                if attack_values:
                    actual_attack = attack_values[0]

            expected_attack = normalize_attack(
                case["attack_type"]
            )

            predicted_attack = normalize_attack(
                actual_attack
            )

            attack_ok = (
                expected_attack == predicted_attack
                or expected_attack in predicted_attack
                or predicted_attack in expected_attack
            )

            if attack_ok:
                attack_correct += 1

            retrieved = get_retrieved_items(
                rag_result
            )

            # Rank retrieved items by their own returned order.
            # Precision/Recall@3 are calculated using whether a chunk
            # contains at least one expected cybersecurity keyword.
            top_k = retrieved[:3]

            relevant_count = 0
            first_relevant_rank = None

            for rank, item in enumerate(
                top_k,
                start=1
            ):
                score = relevance_score(
                    item,
                    case["keywords"]
                )

                if score > 0:
                    relevant_count += 1

                    if first_relevant_rank is None:
                        first_relevant_rank = rank

            precision_at_3 = (
                relevant_count / 3
                if top_k
                else 0
            )

            # Number of expected knowledge concepts represented.
            matched_keywords = set()

            for item in top_k:

                text = normalize(
                    item_text(item)
                )

                for keyword in case["keywords"]:

                    if normalize(keyword) in text:
                        matched_keywords.add(
                            normalize(keyword)
                        )

            recall_at_3 = (
                len(matched_keywords)
                / len(case["keywords"])
                if case["keywords"]
                else 0
            )

            if first_relevant_rank is not None:
                reciprocal_ranks.append(
                    1 / first_relevant_rank
                )
            else:
                reciprocal_ranks.append(0)

            p_at_3_values.append(
                precision_at_3
            )

            recall_at_3_values.append(
                recall_at_3
            )

            # Basic grounding guardrail:
            # Check whether the retrieved context contains the expected
            # attack type or at least one strong incident keyword.
            complete_context = ""

            for item in retrieved:
                complete_context += " " + item_text(item)

            context_lower = normalize(
                complete_context
            )

            attack_grounded = (
                normalize(case["attack_type"])
                in context_lower
                or any(
                    normalize(keyword)
                    in context_lower
                    for keyword in case["keywords"][:3]
                )
            )

            grounding_values.append(
                1 if attack_grounded else 0
            )

            results.append({
                "id": case["id"],
                "latency_seconds": round(
                    elapsed,
                    3
                ),
                "expected_attack": case["attack_type"],
                "predicted_attack": actual_attack or "Not detected",
                "attack_correct": attack_ok,
                "expected_entities": {
                    "PERSON": case["person"],
                    "ORGANIZATION": case["organization"],
                    "LOCATION": case["location"],
                },
                "actual_entities": actual_entities,
                "precision_at_3": round(
                    precision_at_3,
                    3
                ),
                "recall_at_3": round(
                    recall_at_3,
                    3
                ),
                "grounded": attack_grounded,
            })

        except Exception as exc:

            elapsed = time.perf_counter() - start

            results.append({
                "id": case["id"],
                "error": str(exc),
                "latency_seconds": round(
                    elapsed,
                    3
                ),
            })

    successful = [
        r for r in results
        if "error" not in r
    ]

    precision, recall, f1 = entity_metrics(
        successful
    )

    summary = {
        "test_cases": len(TEST_CASES),
        "successful_cases": len(successful),

        "entity_precision": round(
            precision,
            3
        ),

        "entity_recall": round(
            recall,
            3
        ),

        "entity_f1": round(
            f1,
            3
        ),

        "attack_classification_accuracy": round(
            attack_correct / len(successful),
            3
        ) if successful else 0,

        "precision_at_3": round(
            sum(p_at_3_values) / len(p_at_3_values),
            3
        ) if p_at_3_values else 0,

        "recall_at_3": round(
            sum(recall_at_3_values) / len(recall_at_3_values),
            3
        ) if recall_at_3_values else 0,

        "mrr": round(
            sum(reciprocal_ranks) / len(reciprocal_ranks),
            3
        ) if reciprocal_ranks else 0,

        "average_latency_seconds": round(
            sum(latencies) / len(latencies),
            3
        ) if latencies else 0,

        "grounding_rate": round(
            sum(grounding_values) / len(grounding_values),
            3
        ) if grounding_values else 0,
    }

    output = {
        "summary": summary,
        "cases": results,
    }

    output_file = BASE_DIR / "evaluation_results.json"

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            output,
            file,
            indent=4
        )

    if verbose:

        print("\n" + "=" * 65)
        print("CYBERINCIDENT AI - EVALUATION RESULTS")
        print("=" * 65)

        print(
            f"Test Cases                 : "
            f"{summary['test_cases']}"
        )

        print(
            f"Entity Precision           : "
            f"{summary['entity_precision']:.3f}"
        )

        print(
            f"Entity Recall              : "
            f"{summary['entity_recall']:.3f}"
        )

        print(
            f"Entity F1                  : "
            f"{summary['entity_f1']:.3f}"
        )

        print(
            f"Attack Classification Acc. : "
            f"{summary['attack_classification_accuracy']:.3f}"
        )

        print(
            f"Precision@3                : "
            f"{summary['precision_at_3']:.3f}"
        )

        print(
            f"Recall@3                   : "
            f"{summary['recall_at_3']:.3f}"
        )

        print(
            f"MRR                        : "
            f"{summary['mrr']:.3f}"
        )

        print(
            f"Average Latency            : "
            f"{summary['average_latency_seconds']:.3f} sec"
        )

        print(
            f"Context Grounding Rate     : "
            f"{summary['grounding_rate']:.3f}"
        )

        print("=" * 65)

        print(
            f"\nDetailed results saved to:\n"
            f"{output_file}\n"
        )

    return output


if __name__ == "__main__":
    run_evaluation()
