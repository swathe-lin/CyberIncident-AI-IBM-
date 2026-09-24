# ============================================================
# CYBERINCIDENT AI
# Named Entity Recognition (NER)
# ============================================================

import spacy
import re


# ============================================================
# LOAD SPACY MODEL
# ============================================================

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("ERROR: spaCy English model is not installed.")
    print("Run:")
    print("python -m spacy download en_core_web_sm")
    raise


# ============================================================
# CYBERSECURITY ENTITY RULER
# ============================================================

cyber_ruler = nlp.add_pipe(
    "entity_ruler",
    before="ner",
    config={"overwrite_ents": False}
)


patterns = [

    # ---------------- ATTACK TYPES ----------------

    {"label": "ATTACK_TYPE", "pattern": "phishing attack"},
    {"label": "ATTACK_TYPE", "pattern": "phishing"},
    {"label": "ATTACK_TYPE", "pattern": "malware attack"},
    {"label": "ATTACK_TYPE", "pattern": "malware"},
    {"label": "ATTACK_TYPE", "pattern": "ransomware attack"},
    {"label": "ATTACK_TYPE", "pattern": "ransomware"},
    {"label": "ATTACK_TYPE", "pattern": "brute force attack"},
    {"label": "ATTACK_TYPE", "pattern": "brute force"},
    {"label": "ATTACK_TYPE", "pattern": "ddos attack"},
    {"label": "ATTACK_TYPE", "pattern": "denial of service"},
    {"label": "ATTACK_TYPE", "pattern": "sql injection"},
    {"label": "ATTACK_TYPE", "pattern": "data breach"},
    {"label": "ATTACK_TYPE", "pattern": "credential theft"},
    {"label": "ATTACK_TYPE", "pattern": "account takeover"},
    {"label": "ATTACK_TYPE", "pattern": "social engineering"},

    # ---------------- AFFECTED SYSTEMS ----------------

    {"label": "AFFECTED_SYSTEM", "pattern": "email server"},
    {"label": "AFFECTED_SYSTEM", "pattern": "mail server"},
    {"label": "AFFECTED_SYSTEM", "pattern": "web server"},
    {"label": "AFFECTED_SYSTEM", "pattern": "database server"},
    {"label": "AFFECTED_SYSTEM", "pattern": "database"},
    {"label": "AFFECTED_SYSTEM", "pattern": "application server"},
    {"label": "AFFECTED_SYSTEM", "pattern": "network"},
    {"label": "AFFECTED_SYSTEM", "pattern": "firewall"},
    {"label": "AFFECTED_SYSTEM", "pattern": "endpoint"},
    {"label": "AFFECTED_SYSTEM", "pattern": "cloud server"},
    {"label": "AFFECTED_SYSTEM", "pattern": "computer"},
    {"label": "AFFECTED_SYSTEM", "pattern": "laptop"},

    # ---------------- SEVERITY ----------------

    {"label": "SEVERITY", "pattern": "critical severity"},
    {"label": "SEVERITY", "pattern": "high severity"},
    {"label": "SEVERITY", "pattern": "medium severity"},
    {"label": "SEVERITY", "pattern": "low severity"},
    {"label": "SEVERITY", "pattern": "critical"},
    {"label": "SEVERITY", "pattern": "high"},
    {"label": "SEVERITY", "pattern": "medium"},
    {"label": "SEVERITY", "pattern": "low"},

    # ---------------- INDICATORS ----------------

    {"label": "INDICATORS", "pattern": "multiple failed login attempts"},
    {"label": "INDICATORS", "pattern": "failed login"},
    {"label": "INDICATORS", "pattern": "successful login"},
    {"label": "INDICATORS", "pattern": "suspicious login"},
    {"label": "INDICATORS", "pattern": "suspicious link"},
    {"label": "INDICATORS", "pattern": "malicious link"},
    {"label": "INDICATORS", "pattern": "unauthorized access"},
    {"label": "INDICATORS", "pattern": "credential submission"},
    {"label": "INDICATORS", "pattern": "unknown IP"},
    {"label": "INDICATORS", "pattern": "IP address"},
    {"label": "INDICATORS", "pattern": "suspicious activity"},

    # ---------------- ATTACK TECHNIQUES ----------------

    {"label": "ATTACK_TECHNIQUES", "pattern": "credential harvesting"},
    {"label": "ATTACK_TECHNIQUES", "pattern": "credential theft"},
    {"label": "ATTACK_TECHNIQUES", "pattern": "brute force"},
    {"label": "ATTACK_TECHNIQUES", "pattern": "password spraying"},
    {"label": "ATTACK_TECHNIQUES", "pattern": "account takeover"},
    {"label": "ATTACK_TECHNIQUES", "pattern": "social engineering"},
    {"label": "ATTACK_TECHNIQUES", "pattern": "phishing"}
]


cyber_ruler.add_patterns(patterns)


# ============================================================
# ENTITY EXTRACTION FUNCTION
# ============================================================

def extract_entities(text):
    """
    Extract general and cybersecurity-specific
    entities from an incident report.
    """

    doc = nlp(text)

    entities = {
        "PERSON": [],
        "ORGANIZATION": [],
        "LOCATION": [],
        "ATTACK_TYPE": [],
        "AFFECTED_SYSTEM": [],
        "SEVERITY": [],
        "INDICATORS": [],
        "ATTACK_TECHNIQUES": []
    }

    # ========================================================
    # GENERAL AND CYBERSECURITY NER
    # ========================================================

    for ent in doc.ents:

        if ent.label_ == "PERSON":
            entities["PERSON"].append(ent.text)

        elif ent.label_ == "ORG":
            # Prevent false organization detection
            # for email/mail server
            if "email server" not in ent.text.lower() \
                    and "mail server" not in ent.text.lower():
                entities["ORGANIZATION"].append(ent.text)

        elif ent.label_ in ["GPE", "LOC"]:
            entities["LOCATION"].append(ent.text)

        elif ent.label_ == "ATTACK_TYPE":
            entities["ATTACK_TYPE"].append(ent.text)

        elif ent.label_ == "AFFECTED_SYSTEM":
            entities["AFFECTED_SYSTEM"].append(ent.text)

        elif ent.label_ == "SEVERITY":
            entities["SEVERITY"].append(ent.text.upper())

        elif ent.label_ == "INDICATORS":
            entities["INDICATORS"].append(ent.text)

        elif ent.label_ == "ATTACK_TECHNIQUES":
            entities["ATTACK_TECHNIQUES"].append(ent.text)

    # ========================================================
    # ADDITIONAL SECURITY EXTRACTION
    # ========================================================

    text_lower = text.lower()

    # ---------------- ATTACK TYPES ----------------

    attack_types = [
        "phishing attack",
        "phishing",
        "malware attack",
        "malware",
        "ransomware attack",
        "ransomware",
        "brute force attack",
        "brute force",
        "ddos attack",
        "denial of service",
        "sql injection",
        "data breach",
        "credential theft",
        "account takeover",
        "social engineering"
    ]

    for attack in attack_types:
        if attack in text_lower:
            entities["ATTACK_TYPE"].append(attack)

    # ---------------- SEVERITY ----------------

    severity_values = [
        "critical",
        "high",
        "medium",
        "low"
    ]

    for severity in severity_values:
        if re.search(
            r"\b" + re.escape(severity) + r"\b",
            text_lower
        ):
            entities["SEVERITY"].append(severity.upper())

    # ---------------- AFFECTED SYSTEM ----------------

    systems = [
        "email server",
        "mail server",
        "web server",
        "database server",
        "database",
        "application server",
        "network",
        "firewall",
        "endpoint",
        "cloud server",
        "computer",
        "laptop"
    ]

    for system in systems:
        if system in text_lower:
            entities["AFFECTED_SYSTEM"].append(system)

    # ---------------- INDICATORS ----------------

    indicators = [
        "multiple failed login attempts",
        "failed login",
        "successful login",
        "suspicious login",
        "suspicious link",
        "malicious link",
        "unauthorized access",
        "credential submission",
        "unknown ip",
        "ip address",
        "suspicious activity"
    ]

    for indicator in indicators:
        if indicator in text_lower:
            entities["INDICATORS"].append(indicator)

    # ---------------- ATTACK TECHNIQUES ----------------

    techniques = [
        "credential harvesting",
        "credential theft",
        "brute force",
        "password spraying",
        "account takeover",
        "social engineering",
        "phishing"
    ]

    for technique in techniques:
        if technique in text_lower:
            entities["ATTACK_TECHNIQUES"].append(technique)

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    for category in entities:
        entities[category] = list(
            dict.fromkeys(entities[category])
        )

    return entities


# ============================================================
# TEST INCIDENT
# ============================================================

sample_incident = """
John from ABC Corporation reported a phishing attack
affecting the Email Server in Chennai.
The incident was classified as High severity.
The email contained a suspicious login link and resulted
in credential submission.
"""


# ============================================================
# NER TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CYBERINCIDENT AI - NER TEST")
    print("=" * 60)

    results = extract_entities(sample_incident)

    for category, values in results.items():

        if values:

            print(f"\n{category}:")

            for value in values:
                print(f" - {value}")

    print("\n" + "=" * 60)
    print("NER TEST COMPLETED")
    print("=" * 60)