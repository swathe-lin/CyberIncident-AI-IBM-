import streamlit as st
from pathlib import Path
import sys
import re
import json
import csv
import io


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# PROJECT MODULES
# ============================================================

from rag import build_rag_context
import gemini_llm


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CyberIncident AI",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# GLOBAL STYLE
# ============================================================

st.markdown(
    """
<style>

.stApp {
    background:
        radial-gradient(
            circle at top right,
            #102a43 0%,
            #07121e 42%,
            #050a10 82%
        );
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

html,
body,
[class*="css"] {
    font-family: "Segoe UI", "Inter", Arial, sans-serif;
}

#MainMenu {
    visibility: hidden;
}

header {
    visibility: hidden;
}


/* ==========================================================
   HEADINGS
   ========================================================== */

h1 {
    font-weight: 800 !important;
    letter-spacing: -0.5px;
}

h2 {
    font-weight: 750 !important;
}

h3 {
    font-weight: 700 !important;
}


/* ==========================================================
   INCIDENT OVERVIEW METRICS
   ========================================================== */

[data-testid="stMetric"] {
    background:
        linear-gradient(
            145deg,
            #111f30,
            #0b1521
        );

    border: 1px solid #29425a;
    border-radius: 16px;

    padding: 16px 18px;

    min-height: 118px;

    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
}

[data-testid="stMetricLabel"] {
    font-size: 13px !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    font-size: 19px !important;
    font-weight: 700 !important;

    white-space: normal !important;
    overflow-wrap: break-word !important;
    word-break: normal !important;

    line-height: 1.2 !important;

    min-height: 48px !important;

    display: flex !important;
    align-items: center !important;
}


/* ==========================================================
   BUTTONS
   ========================================================== */

.stButton > button {
    width: 100%;
    min-height: 48px;

    border-radius: 12px;

    font-weight: 750;
}


/* ==========================================================
   TEXT AREA
   ========================================================== */

textarea {
    border-radius: 14px !important;
}


/* ==========================================================
   EXPANDERS
   ========================================================== */

[data-testid="stExpander"] {
    background: #0b141f;
    border: 1px solid #263b50;
    border-radius: 13px;
}


/* ==========================================================
   FOOTER
   ========================================================== */

.footer {
    text-align: center;
    color: #718397;

    font-size: 12px;

    padding: 25px 0 5px;

    margin-top: 40px;

    border-top: 1px solid #1d2b39;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# ATTACK CLASSIFICATION
# ============================================================

ATTACK_PATTERNS = [

    (
        "Ransomware Attack",
        [
            "ransomware",
            "ransom note",
            "files were encrypted",
            "files encrypted",
            "data encrypted",
            "encrypted files",
            "crypto locker",
            "cryptolocker",
            "demanded ransom",
            "ransom demand"
        ]
    ),

    (
        "Phishing Attack",
        [
            "phishing",
            "phishing email",
            "fake login page",
            "fake login website",
            "fake website",
            "malicious email",
            "suspicious email",
            "credential harvesting",
            "credential theft",
            "deceptive email"
        ]
    ),

    (
        "Spear Phishing Attack",
        [
            "spear phishing",
            "targeted phishing",
            "targeted email attack"
        ]
    ),

    (
        "SQL Injection",
        [
            "sql injection",
            "sql attack",
            "sql payload",
            "union select",
            "database injection",
            "malicious sql statement"
        ]
    ),

    (
        "Cross-Site Scripting (XSS)",
        [
            "cross-site scripting",
            "cross site scripting",
            "xss attack",
            "xss payload",
            "javascript payload"
        ]
    ),

    (
        "DDoS Attack",
        [
            "ddos",
            "distributed denial of service",
            "distributed denial-of-service",
            "traffic flood",
            "network flood",
            "application flood",
            "overwhelming traffic"
        ]
    ),

    (
        "DoS Attack",
        [
            "denial of service",
            "denial-of-service",
            "dos attack",
            "service unavailable",
            "service disruption"
        ]
    ),

    (
        "Brute Force Attack",
        [
            "brute force",
            "brute-force",
            "multiple failed login",
            "multiple failed logins",
            "repeated failed login",
            "repeated failed logins",
            "repeated login attempts",
            "repeated authentication attempts",
            "password guessing",
            "credential guessing",
            "many failed authentication attempts"
        ]
    ),

    (
        "Credential Stuffing Attack",
        [
            "credential stuffing",
            "stolen credentials",
            "reused credentials",
            "credential reuse",
            "login attempts using stolen credentials"
        ]
    ),

    (
        "Password Spraying Attack",
        [
            "password spraying",
            "password spray",
            "password spray attack"
        ]
    ),

    (
        "Malware Attack",
        [
            "malware",
            "malicious software",
            "malicious executable",
            "malicious file",
            "malware infection",
            "infected system",
            "infected workstation",
            "malicious program"
        ]
    ),

    (
        "Trojan Attack",
        [
            "trojan",
            "trojan horse"
        ]
    ),

    (
        "Spyware Attack",
        [
            "spyware",
            "keylogger",
            "key logging",
            "keystroke logging"
        ]
    ),

    (
        "Worm Attack",
        [
            "computer worm",
            "network worm",
            "worm infection"
        ]
    ),

    (
        "Command Injection",
        [
            "command injection",
            "os command injection",
            "shell injection",
            "arbitrary command execution"
        ]
    ),

    (
        "Privilege Escalation",
        [
            "privilege escalation",
            "elevated privileges",
            "administrator privileges",
            "admin privileges",
            "unauthorized privilege"
        ]
    ),

    (
        "Data Exfiltration",
        [
            "data exfiltration",
            "data theft",
            "stolen data",
            "sensitive data transferred",
            "unauthorized data transfer",
            "data was transferred"
        ]
    ),

    (
        "Man-in-the-Middle Attack",
        [
            "man-in-the-middle",
            "man in the middle",
            "mitm attack",
            "traffic interception",
            "intercepted communication"
        ]
    ),

    (
        "Port Scanning",
        [
            "port scan",
            "port scanning",
            "scanned multiple ports",
            "open port discovery",
            "network reconnaissance"
        ]
    ),

    (
        "Account Takeover",
        [
            "account takeover",
            "account compromised",
            "compromised account",
            "unauthorized account access",
            "attacker accessed the account"
        ]
    ),

    (
        "Insider Threat",
        [
            "insider threat",
            "malicious employee",
            "employee misuse",
            "unauthorized employee activity"
        ]
    ),

    (
        "DNS Attack",
        [
            "dns attack",
            "dns poisoning",
            "dns spoofing",
            "dns hijacking"
        ]
    ),

    (
        "ARP Spoofing",
        [
            "arp spoofing",
            "arp poisoning",
            "arp attack"
        ]
    ),

    (
        "IP Spoofing",
        [
            "ip spoofing",
            "spoofed ip",
            "spoofed source ip"
        ]
    ),

    (
        "Session Hijacking",
        [
            "session hijacking",
            "session takeover",
            "stolen session",
            "session token theft"
        ]
    ),

    (
        "Web Shell Attack",
        [
            "web shell",
            "webshell",
            "web shell attack"
        ]
    ),

    (
        "Supply Chain Attack",
        [
            "supply chain attack",
            "compromised dependency",
            "malicious dependency",
            "third party compromise"
        ]
    )
]


def detect_attack_type(incident_text, extracted_attack_types=None):

    """
    Determine attack type using:
    1. Complete incident text
    2. Strong keyword/pattern matching
    3. NER output
    4. Generic security classification fallback
    """

    text = incident_text.lower()

    # --------------------------------------------------------
    # Exact / strong pattern detection
    # --------------------------------------------------------

    matches = []

    for attack_name, keywords in ATTACK_PATTERNS:

        score = 0

        for keyword in keywords:

            if keyword in text:
                score += 1

        if score > 0:

            matches.append(
                (
                    score,
                    attack_name
                )
            )

    if matches:

        matches.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return matches[0][1]

    # --------------------------------------------------------
    # NER fallback
    # --------------------------------------------------------

    if extracted_attack_types:

        for value in extracted_attack_types:

            value = str(value).strip()

            if not value:
                continue

            lower = value.lower()

            if "brute force" in lower:
                return "Brute Force Attack"

            if "phishing" in lower:
                return "Phishing Attack"

            if "ransomware" in lower:
                return "Ransomware Attack"

            if "malware" in lower:
                return "Malware Attack"

            if "sql injection" in lower:
                return "SQL Injection"

            if "ddos" in lower:
                return "DDoS Attack"

            if "denial of service" in lower:
                return "DoS Attack"

            return value.title()

    # --------------------------------------------------------
    # Suspicious activity fallback
    # --------------------------------------------------------

    suspicious_terms = [
        "unauthorized access",
        "suspicious login",
        "suspicious activity",
        "security incident",
        "unauthorized activity",
        "compromised account",
        "malicious activity",
        "security breach",
        "cyber attack",
        "cyberattack",
        "intrusion"
    ]

    for term in suspicious_terms:

        if term in text:

            return "Suspicious / Unauthorized Activity"

    return "Security Incident"


# ============================================================
# SEVERITY DETECTION
# ============================================================

def detect_severity(incident_text, extracted_severities=None):

    text = incident_text.lower()

    # Explicit severity has highest priority
    severity_patterns = [
        (r"\bcritical severity\b", "CRITICAL"),
        (r"\bcritical\b", "CRITICAL"),
        (r"\bhigh severity\b", "HIGH"),
        (r"\bhigh\b", "HIGH"),
        (r"\bmedium severity\b", "MEDIUM"),
        (r"\bmedium\b", "MEDIUM"),
        (r"\blow severity\b", "LOW"),
        (r"\blow\b", "LOW")
    ]

    for pattern, value in severity_patterns:

        if re.search(pattern, text):

            return value

    if extracted_severities:

        value = str(
            extracted_severities[0]
        ).strip().upper()

        if value in [
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW"
        ]:

            return value

    # Infer only when the incident clearly contains strong
    # evidence of compromise.

    if any(
        phrase in text
        for phrase in [
            "ransomware",
            "data exfiltration",
            "data breach",
            "system compromise",
            "account takeover"
        ]
    ):

        return "HIGH"

    return "Not Specified"


# ============================================================
# AFFECTED SYSTEM DETECTION
# ============================================================

SYSTEM_PATTERNS = [

    (r"\bvpn server\b", "VPN Server"),
    (r"\bvpn\b", "VPN Server"),

    (r"\bemail server\b", "Email Server"),
    (r"\bmail server\b", "Mail Server"),
    (r"\bemail system\b", "Email System"),

    (r"\bweb server\b", "Web Server"),
    (r"\bweb application\b", "Web Application"),
    (r"\bwebsite\b", "Web Application"),

    (r"\bdatabase server\b", "Database Server"),
    (r"\bdatabase\b", "Database"),

    (r"\bfile server\b", "File Server"),
    (r"\bfile system\b", "File System"),

    (r"\bcloud server\b", "Cloud Server"),
    (r"\bcloud system\b", "Cloud System"),

    (r"\bfirewall\b", "Firewall"),
    (r"\brouter\b", "Router"),
    (r"\bswitch\b", "Network Switch"),

    (r"\bworkstation\b", "Workstation"),
    (r"\bdesktop\b", "Workstation"),
    (r"\blaptop\b", "Laptop"),
    (r"\bcomputer\b", "Computer"),

    (r"\bendpoint\b", "Endpoint"),

    (r"\bapi\b", "API"),
    (r"\bserver\b", "Server"),
    (r"\bapplication\b", "Application"),
    (r"\bnetwork\b", "Network")
]


def detect_affected_system(
    incident_text,
    extracted_systems
):

    text = incident_text.lower()

    for pattern, name in SYSTEM_PATTERNS:

        if re.search(pattern, text):

            return name

    if extracted_systems:

        value = str(
            extracted_systems[0]
        ).strip()

        if value:

            return value.title()

    return "Not Specified"


# ============================================================
# IP EXTRACTION
# ============================================================

def extract_ips(text):

    ips = re.findall(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        text
    )

    valid = []

    for ip in ips:

        parts = ip.split(".")

        if len(parts) != 4:
            continue

        try:

            if all(
                0 <= int(part) <= 255
                for part in parts
            ):

                if ip not in valid:
                    valid.append(ip)

        except ValueError:
            continue

    return valid


# ============================================================
# INDICATOR CLEANING
# ============================================================

def clean_indicators(
    indicators,
    incident_text
):

    candidates = []

    # --------------------------------------------------------
    # Real IP addresses
    # --------------------------------------------------------

    for ip in extract_ips(incident_text):

        if ip not in candidates:

            candidates.append(ip)

    # --------------------------------------------------------
    # NER indicators
    # --------------------------------------------------------

    for item in indicators:

        item = str(item).strip()

        if not item:
            continue

        lower = item.lower()

        # Remove generic labels
        if lower in [
            "ip",
            "ip address",
            "source ip",
            "source ip address",
            "indicator",
            "indicators"
        ]:

            continue

        # Don't add duplicate IP labels
        if re.fullmatch(
            r"(?:\d{1,3}\.){3}\d{1,3}",
            item
        ):

            if item not in candidates:
                candidates.append(item)

            continue

        # Add only if unique
        if not any(
            item.lower() == existing.lower()
            for existing in candidates
        ):

            candidates.append(item)

    # --------------------------------------------------------
    # Remove exact duplicates
    # --------------------------------------------------------

    unique = []

    for item in candidates:

        if not any(
            item.lower() == existing.lower()
            for existing in unique
        ):

            unique.append(item)

    # --------------------------------------------------------
    # Remove shorter overlapping phrases
    # --------------------------------------------------------

    final = []

    for item in unique:

        item_lower = item.lower().strip()

        redundant = False

        for other in unique:

            other_lower = other.lower().strip()

            if item_lower == other_lower:
                continue

            if (
                item_lower in other_lower
                and len(other_lower) > len(item_lower)
            ):

                redundant = True
                break

        if not redundant:

            final.append(item)

    return final


# ============================================================
# POSSIBLE IMPACT
# ============================================================

def get_possible_impact(
    attack_type,
    affected_system
):

    attack = attack_type.lower()

    if "brute force" in attack:

        return (
            f"Repeated authentication attempts against the "
            f"{affected_system} may result in unauthorized "
            "account access if successful."
        )

    if "phishing" in attack:

        return (
            "User credentials or sensitive information may have "
            "been exposed, potentially enabling unauthorized "
            "account access."
        )

    if "ransomware" in attack:

        return (
            "Systems or files may become unavailable due to "
            "encryption, potentially causing operational "
            "disruption and data loss."
        )

    if "sql injection" in attack:

        return (
            f"The {affected_system} may be exposed to unauthorized "
            "database access, modification, or data disclosure."
        )

    if "ddos" in attack or attack == "dos attack":

        return (
            f"The {affected_system} may experience service "
            "degradation or complete unavailability."
        )

    if "malware" in attack:

        return (
            "The affected system may experience unauthorized "
            "activity, data exposure, persistence, or further "
            "network compromise."
        )

    if "data exfiltration" in attack:

        return (
            "Sensitive organizational or user information may "
            "have been transferred to an unauthorized destination."
        )

    if "privilege escalation" in attack:

        return (
            "An attacker may gain elevated permissions and access "
            "resources beyond the originally compromised account."
        )

    if "account takeover" in attack:

        return (
            "The compromised account may be used for unauthorized "
            "access, data exposure, or additional malicious activity."
        )

    if "suspicious" in attack.lower():

        return (
            "The observed activity may indicate unauthorized access "
            "or attempted compromise. Further investigation is "
            "required to determine the actual impact."
        )

    return (
        f"The incident may affect the {affected_system} through "
        "unauthorized access, disruption, data exposure, or "
        "additional malicious activity depending on the findings."
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

def get_recommendations(
    attack_type,
    indicators
):

    attack = attack_type.lower()

    recommendations = []

    if "brute force" in attack:

        recommendations = [
            "Investigate the affected account and successful login activity.",
            "Block or monitor the suspicious source IP.",
            "Reset credentials for the affected account.",
            "Enable Multi-Factor Authentication (MFA).",
            "Review authentication logs for related attempts."
        ]

    elif "phishing" in attack:

        recommendations = [
            "Investigate the affected account and email activity.",
            "Reset potentially exposed credentials.",
            "Enable Multi-Factor Authentication (MFA).",
            "Block malicious links, domains, or sender addresses.",
            "Review authentication and email security logs."
        ]

    elif "ransomware" in attack:

        recommendations = [
            "Isolate affected systems from the network.",
            "Preserve evidence and investigate the initial infection vector.",
            "Verify the integrity of available backups.",
            "Reset potentially compromised credentials.",
            "Monitor the environment for additional infected systems."
        ]

    elif "sql injection" in attack:

        recommendations = [
            "Review and block malicious requests.",
            "Validate and sanitize application input.",
            "Use parameterized queries or prepared statements.",
            "Review database access logs.",
            "Investigate whether unauthorized data was accessed."
        ]

    elif "ddos" in attack or attack == "dos attack":

        recommendations = [
            "Identify and filter malicious traffic sources.",
            "Enable appropriate network or application-level DDoS protection.",
            "Monitor traffic volume and affected services.",
            "Review firewall and network security logs.",
            "Verify service availability after mitigation."
        ]

    elif "malware" in attack:

        recommendations = [
            "Isolate the affected endpoint or system.",
            "Identify and preserve the malicious file or process.",
            "Run endpoint security scans.",
            "Review network connections and persistence mechanisms.",
            "Monitor other systems for related activity."
        ]

    elif "data exfiltration" in attack:

        recommendations = [
            "Identify the affected data and destination.",
            "Block unauthorized transfer channels.",
            "Review data access and network logs.",
            "Reset credentials if account compromise is suspected.",
            "Assess the scope of potentially exposed information."
        ]

    else:

        recommendations = [
            "Investigate the affected system and user activity.",
            "Review relevant security and authentication logs.",
            "Preserve evidence for further investigation.",
            "Reset potentially compromised credentials.",
            "Continue monitoring for related activity."
        ]

    return recommendations


# ============================================================
# INCIDENT SUMMARY
# ============================================================

def create_summary(
    attack_type,
    affected_system,
    severity,
    incident_text
):

    attack = attack_type.lower()

    if "brute force" in attack:

        return (
            f"Repeated authentication activity was identified "
            f"against the {affected_system}. The observed activity "
            f"is consistent with a brute force attack and is "
            f"classified as {severity} severity."
        )

    if "phishing" in attack:

        return (
            f"Phishing-related activity was identified involving "
            f"the {affected_system}. The incident is classified as "
            f"{severity} severity."
        )

    if "ransomware" in attack:

        return (
            f"Ransomware-related activity was identified affecting "
            f"the {affected_system}. The incident is classified as "
            f"{severity} severity."
        )

    if "sql injection" in attack:

        return (
            f"SQL injection activity was identified against the "
            f"{affected_system}. The incident is classified as "
            f"{severity} severity."
        )

    if "malware" in attack:

        return (
            f"Malware-related activity was identified on the "
            f"{affected_system}. The incident is classified as "
            f"{severity} severity."
        )

    return (
        f"{attack_type} activity was identified involving the "
        f"{affected_system}. The reported severity is "
        f"{severity}."
    )


# ============================================================
# FILE READING
# ============================================================

def read_uploaded_file(uploaded_file):

    extension = Path(
        uploaded_file.name
    ).suffix.lower()

    raw = uploaded_file.read()

    # --------------------------------------------------------
    # TXT / LOG
    # --------------------------------------------------------

    if extension in [
        ".txt",
        ".log"
    ]:

        return raw.decode(
            "utf-8",
            errors="ignore"
        )

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    if extension == ".json":

        try:

            data = json.loads(
                raw.decode(
                    "utf-8",
                    errors="ignore"
                )
            )

            return json.dumps(
                data,
                indent=2
            )

        except Exception:

            return raw.decode(
                "utf-8",
                errors="ignore"
            )

    # --------------------------------------------------------
    # CSV
    # --------------------------------------------------------

    if extension == ".csv":

        try:

            text = raw.decode(
                "utf-8",
                errors="ignore"
            )

            reader = csv.reader(
                io.StringIO(text)
            )

            rows = list(reader)

            return "\n".join(
                " | ".join(row)
                for row in rows
            )

        except Exception:

            return raw.decode(
                "utf-8",
                errors="ignore"
            )

    return raw.decode(
        "utf-8",
        errors="ignore"
    )


# ============================================================
# HERO
# ============================================================

st.title("🔐 CyberIncident AI")

st.subheader(
    "AI-Powered Cybersecurity Incident Analysis & Intelligence"
)


# ============================================================
# INCIDENT INPUT
# ============================================================

st.header(
    "📋 Enter / Upload Incident Report"
)

st.caption(
    "Enter the actual incident details or upload an incident report file."
)


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "📎 Upload Incident Report",
    type=[
        "txt",
        "log",
        "csv",
        "json"
    ],
    help="Upload the actual incident report for analysis."
)


uploaded_text = ""


if uploaded_file is not None:

    try:

        uploaded_text = read_uploaded_file(
            uploaded_file
        )

        st.success(
            f"✓ {uploaded_file.name} uploaded successfully"
        )

    except Exception as error:

        st.error(
            f"Unable to read uploaded file: {error}"
        )


# ============================================================
# INCIDENT TEXT INPUT
# ============================================================

incident_text = st.text_area(
    "Incident Details",
    value=uploaded_text,
    height=180,
    placeholder=(
        "Example:\n\n"
        "Multiple failed authentication attempts were detected "
        "against the VPN server from IP address 185.199.110.25. "
        "The activity was followed by a successful login from "
        "an unusual location. The employee did not recognize "
        "the login and the incident was classified as HIGH severity."
    )
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze = st.button(
    "🔎 Analyze Incident",
    type="primary"
)


# ============================================================
# ANALYSIS
# ============================================================

if analyze:

    if not incident_text.strip():

        st.warning(
            "⚠️ Please enter or upload an incident report first."
        )

        st.stop()


    # ========================================================
    # RAG
    # ========================================================

    with st.spinner(
        "🔍 Analyzing incident..."
    ):

        try:

            rag_result = build_rag_context(
                incident_text
            )

        except Exception as error:

            st.error(
                f"RAG processing failed: {error}"
            )

            st.stop()


    # ========================================================
    # EXTRACT ENTITIES
    # ========================================================

    entities = rag_result.get(
        "entities",
        {}
    )


    attack_types = list(
        dict.fromkeys(
            entities.get(
                "ATTACK_TYPE",
                []
            )
        )
    )


    severities = list(
        dict.fromkeys(
            entities.get(
                "SEVERITY",
                []
            )
        )
    )


    affected_systems = list(
        dict.fromkeys(
            entities.get(
                "AFFECTED_SYSTEM",
                []
            )
        )
    )


    raw_indicators = entities.get(
        "INDICATORS",
        []
    )


    # ========================================================
    # FINAL CLASSIFICATION
    # ========================================================

    attack_type = detect_attack_type(
        incident_text,
        attack_types
    )


    severity = detect_severity(
        incident_text,
        severities
    )


    affected_system = detect_affected_system(
        incident_text,
        affected_systems
    )


    indicators = clean_indicators(
        raw_indicators,
        incident_text
    )


    # ========================================================
    # INCIDENT OVERVIEW
    # ========================================================

    st.header(
        "📊 Incident Overview"
    )


    col1, col2, col3, col4 = st.columns(
        [1, 1.35, 1.15, 0.8]
    )


    with col1:

        st.metric(
            "🚨 Severity",
            severity
        )


    with col2:

        st.metric(
            "🎯 Attack Type",
            attack_type
        )


    with col3:

        st.metric(
            "🖥️ Affected System",
            affected_system
        )


    with col4:

        st.metric(
            "🔎 Indicators",
            len(indicators)
        )


    # ========================================================
    # EXTRACTED ENTITIES
    # ========================================================

    st.header(
        "🧩 Extracted Entities"
    )


    left, right = st.columns(2)


    with left:

        with st.container(border=True):

            st.subheader(
                "🧠 Attack Information"
            )

            st.write(
                f"**Attack Type:** {attack_type}"
            )

            st.write(
                f"**Severity:** {severity}"
            )

            st.write(
                f"**Affected System:** {affected_system}"
            )


    with right:

        with st.container(border=True):

            st.subheader(
                "🔎 Security Indicators"
            )

            if indicators:

                for indicator in indicators:

                    st.write(
                        f"• {indicator}"
                    )

            else:

                st.info(
                    "No specific security indicators detected."
                )


    # ========================================================
    # RETRIEVED KNOWLEDGE
    # ========================================================

    st.header(
        "📚 Retrieved Cybersecurity Knowledge"
    )


    retrieved = rag_result.get(
        "retrieved_knowledge",
        []
    )


    if retrieved:

        for index, result in enumerate(
            retrieved,
            start=1
        ):

            score = result.get(
                "score",
                0
            )

            source_text = result.get(
                "text",
                ""
            ).strip()


            source_text = re.sub(
                r"={3,}",
                "",
                source_text
            ).strip()


            with st.expander(
                f"📘 Source {index} • Similarity: {score:.4f}"
            ):

                st.markdown(
                    f"**🛡️ Cybersecurity Knowledge {index}**"
                )

                st.write(
                    source_text
                )

    else:

        st.info(
            "No matching cybersecurity knowledge was retrieved."
        )


    # ========================================================
    # AI-GENERATED INCIDENT ANALYSIS
    # ========================================================

    st.header(
        "🤖 AI-Generated Incident Analysis"
    )


    summary = create_summary(
        attack_type,
        affected_system,
        severity,
        incident_text
    )


    impact = get_possible_impact(
        attack_type,
        affected_system
    )


    recommendations = get_recommendations(
        attack_type,
        indicators
    )


    # ========================================================
    # INCIDENT SUMMARY
    # ========================================================

    st.subheader(
        "📌 Incident Summary"
    )

    st.info(
        summary
    )


    # ========================================================
    # EXTRACTED INFORMATION
    # ========================================================

    st.subheader(
        "🔍 Extracted Information"
    )


    ip_addresses = extract_ips(
        incident_text
    )


    ip_text = (
        ", ".join(ip_addresses)
        if ip_addresses
        else "Not detected"
    )


    info1, info2, info3 = st.columns(3)


    with info1:

        st.metric(
            "🎯 Attack Type",
            attack_type
        )


    with info2:

        st.metric(
            "🖥️ Affected System",
            affected_system
        )


    with info3:

        st.metric(
            "🌐 Source IP",
            ip_text
        )


    st.write(
        f"**Severity:** {severity}"
    )


    st.write(
        "**Key Indicators:** "
        + (
            ", ".join(indicators)
            if indicators
            else "None detected"
        )
    )


    # ========================================================
    # POSSIBLE IMPACT
    # ========================================================

    st.subheader(
        "⚠️ Possible Impact"
    )

    st.warning(
        impact
    )


    # ========================================================
    # RECOMMENDED ACTIONS
    # ========================================================

    st.subheader(
        "⚡ Recommended Actions"
    )


    for index, recommendation in enumerate(
        recommendations,
        start=1
    ):

        st.write(
            f"**{index}.** {recommendation}"
        )


    # ========================================================
    # GEMINI DETAILED ANALYSIS
    # ========================================================

    detailed_analysis = ""


    try:

        if hasattr(
            gemini_llm,
            "generate_incident_analysis"
        ):

            detailed_analysis = (
                gemini_llm.generate_incident_analysis(
                    incident_text,
                    rag_result
                )
            )

    except Exception as error:

        detailed_analysis = ""


    if detailed_analysis:

        with st.expander(
            "✨ View Detailed Gemini Analysis"
        ):

            st.markdown(
                detailed_analysis
            )


    # ========================================================
    # COMPLETE RAG CONTEXT
    # ========================================================

    with st.expander(
        "🔍 View Complete RAG Context"
    ):

        st.code(
            rag_result.get(
                "rag_context",
                ""
            ),
            language="text"
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="footer">
🔐 CyberIncident AI • AI-Powered Cybersecurity Incident Analysis
</div>
""",
    unsafe_allow_html=True
)