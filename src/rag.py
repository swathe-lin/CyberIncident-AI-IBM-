# ============================================================
# CYBERINCIDENT AI
# RAG CONTEXT BUILDER
# ============================================================

import sys
from pathlib import Path


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# IMPORT EXISTING MODULES
# ============================================================

from preprocessing import clean_text
from ner import extract_entities
from tfidf_retrieval import retrieve_relevant_knowledge


# ============================================================
# BUILD RAG CONTEXT
# ============================================================

def build_rag_context(incident_text):
    """
    Build grounded context for the Gemini LLM.

    The context contains:
    1. Original incident
    2. Extracted entities
    3. Retrieved cybersecurity knowledge
    """

    # --------------------------------------------------------
    # 1. CLEAN INCIDENT
    # --------------------------------------------------------

    cleaned_incident = clean_text(incident_text)

    # --------------------------------------------------------
    # 2. EXTRACT ENTITIES
    # --------------------------------------------------------

    entities = extract_entities(cleaned_incident)

    # --------------------------------------------------------
    # 3. RETRIEVE RELEVANT KNOWLEDGE
    # --------------------------------------------------------

    retrieved_knowledge = retrieve_relevant_knowledge(
        cleaned_incident,
        top_k=3
    )

    # --------------------------------------------------------
    # 4. BUILD CONTEXT
    # --------------------------------------------------------

    context_parts = []

    context_parts.append(
        "=== INCIDENT REPORT ===\n"
        + cleaned_incident
    )

    # --------------------------------------------------------
    # 5. ADD EXTRACTED ENTITIES
    # --------------------------------------------------------

    entity_text = "\n=== EXTRACTED ENTITIES ==="

    for category, values in entities.items():

        if values:

            entity_text += f"\n{category}: "

            entity_text += ", ".join(values)

    context_parts.append(entity_text)

    # --------------------------------------------------------
    # 6. ADD RETRIEVED KNOWLEDGE
    # --------------------------------------------------------

    knowledge_text = "\n=== RETRIEVED CYBERSECURITY KNOWLEDGE ==="

    for i, result in enumerate(
        retrieved_knowledge,
        start=1
    ):

        knowledge_text += (
            f"\n\n--- SOURCE {i} ---\n"
        )

        knowledge_text += (
            f"Similarity Score: "
            f"{result['score']:.4f}\n"
        )

        knowledge_text += result["text"]

    context_parts.append(knowledge_text)

    # --------------------------------------------------------
    # 7. COMBINE EVERYTHING
    # --------------------------------------------------------

    rag_context = "\n".join(context_parts)

    return {
        "incident": cleaned_incident,
        "entities": entities,
        "retrieved_knowledge": retrieved_knowledge,
        "rag_context": rag_context
    }


# ============================================================
# TEST RAG
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CYBERINCIDENT AI - RAG CONTEXT TEST")
    print("=" * 60)

    test_incident = """
    Multiple failed login attempts were detected from
    IP address 185.199.110.25 on the VPN server.
    The activity was followed by a successful login from
    a suspicious location.
    The incident indicates a possible brute force attack
    targeting an employee account.
    The severity of the incident is high.
    """

    result = build_rag_context(test_incident)

    print("\n")
    print(result["rag_context"])

    print("\n" + "=" * 60)
    print("RAG CONTEXT TEST COMPLETED")
    print("=" * 60)