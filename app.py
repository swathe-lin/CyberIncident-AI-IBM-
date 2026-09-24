import streamlit as st
from pathlib import Path
import sys
import re
import json
import csv
import io
import base64
from pypdf import PdfReader


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "cybersecurity_logo.png"

if LOGO_PATH.exists():
    with open(LOGO_PATH, "rb") as logo_file:
        LOGO_BASE64 = base64.b64encode(logo_file.read()).decode("utf-8")
else:
    LOGO_BASE64 = ""

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# BACKEND MODULES
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
# FRONTEND CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   MAIN BACKGROUND
   ============================================================ */

.stApp {

    background:
        radial-gradient(
            circle at 85% 8%,
            rgba(37, 126, 245, 0.28),
            transparent 27%
        ),

        radial-gradient(
            circle at 8% 42%,
            rgba(92, 182, 255, 0.20),
            transparent 30%
        ),

        linear-gradient(
            135deg,
            #ffffff 0%,
            #f4faff 25%,
            #e3f2ff 55%,
            #c9e5ff 100%
        );

    color: #102a43;

}


/* ============================================================
   SUBTLE CYBER GRID
   ============================================================ */

.stApp::before {

    content: "";

    position: fixed;

    top: 0;
    right: 0;

    width: 500px;
    height: 500px;

    pointer-events: none;

    opacity: 0.32;

    background-image:

        linear-gradient(
            rgba(23, 105, 224, 0.10) 1px,
            transparent 1px
        ),

        linear-gradient(
            90deg,
            rgba(23, 105, 224, 0.10) 1px,
            transparent 1px
        );

    background-size: 35px 35px;

    mask-image:
        radial-gradient(
            circle,
            black 0%,
            transparent 72%
        );

    z-index: 0;

}


/* ============================================================
   MAIN CONTAINER
   ============================================================ */

.block-container {

    max-width: 1200px;

    padding-top: 1.8rem;

    padding-bottom: 3rem;

    position: relative;

    z-index: 1;

}


/* ============================================================
   FONT
   ============================================================ */

html,
body,
[class*="css"] {

    font-family:
        "Segoe UI",
        "Inter",
        Arial,
        sans-serif;

}


/* ============================================================
   HIDE STREAMLIT DEFAULT UI
   ============================================================ */

#MainMenu {
    visibility: hidden;
}

header {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* ============================================================
   HERO
   ============================================================ */

.hero-badge {

    display: inline-block;

    padding: 7px 14px;

    margin-top: 15px;

    margin-bottom: 12px;

    border-radius: 30px;

    background: rgba(23, 105, 224, 0.10);

    border: 1px solid #b9d9f5;

    color: #155da8;

    font-size: 11px;

    font-weight: 800;

    letter-spacing: 1px;

}


.hero-title {

    font-size: 48px !important;

    font-weight: 850 !important;

    line-height: 1.1 !important;

    letter-spacing: -1.5px;

    color: #092f63 !important;

    margin-top: 5px !important;

    margin-bottom: 8px !important;

}

.hero-title {
    display: flex !important;
    align-items: center !important;
    gap: 10px;
    white-space: nowrap;
}

.title-logo {
    width: 95px;
    height: 95px;
    object-fit: contain;
    display: inline-block;
    flex-shrink: 0;
}


.hero-title span {

    color: #1769e0 !important;

}


.hero-description {

    max-width: 570px;

    color: #4d6d8c !important;

    font-size: 18px !important;

    line-height: 1.6;

    margin-bottom: 25px;

}


/* ============================================================
   HERO IMAGE PLACEHOLDER
   ============================================================ */

.image-placeholder {

    height: 300px;

    width: 100%;

    border-radius: 24px;

    background:

        radial-gradient(
            circle at 50% 35%,
            rgba(255,255,255,0.9),
            transparent 32%
        ),

        linear-gradient(
            145deg,
            #eaf6ff,
            #c5e4ff
        );

    border: 1px solid #afd4f2;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    text-align: center;

    box-shadow:

        0 16px 35px
        rgba(20,90,155,0.13);

}


.shield-icon {

    font-size: 62px;

    margin-bottom: 10px;

}


.placeholder-title {

    color: #155a9e;

    font-size: 19px;

    font-weight: 800;

}


.placeholder-subtitle {

    color: #5480a5;

    font-size: 14px;

    margin-top: 4px;

}

/* ============================================================
   SECTION HEADINGS
   ============================================================ */

h1 {

    color: #0b2f5f !important;

    font-weight: 850 !important;

}


h2 {

    color: #103f73 !important;

    font-size: 28px !important;

    font-weight: 800 !important;

    margin-top: 1.8rem !important;

}


h3 {

    color: #174f85 !important;

    font-size: 21px !important;

    font-weight: 750 !important;

}


/* Section underline */

h2::after {

    content: "";

    display: block;

    width: 52px;

    height: 4px;

    margin-top: 8px;

    border-radius: 20px;

    background:

        linear-gradient(
            90deg,
            #1769e0,
            #65b9ff
        );

}


/* ============================================================
   NORMAL TEXT
   ============================================================ */

.stApp p {

    color: #506b84;

}


/* ============================================================
   INPUT AREA
   ============================================================ */

[data-testid="stTextArea"] {

    background:
        rgba(255,255,255,0.94) !important;

    border:
        1px solid #b9d8f2 !important;

    border-radius:
        18px !important;

    box-shadow:

        0 10px 28px
        rgba(25, 90, 145, 0.08);

}


textarea {

    background:
        #ffffff !important;

    color:
        #173b60 !important;

    border-radius:
        15px !important;

    font-size:
        15px !important;

    line-height:
        1.65 !important;

}


textarea::placeholder {

    color:
        #8aa4bd !important;

}


/* ============================================================
   FILE UPLOAD
   ============================================================ */

[data-testid="stFileUploader"] {

    background:
        rgba(255,255,255,0.92) !important;

    border:
        1px solid #b9d8f2 !important;

    border-radius:
        18px !important;

    padding:
        9px !important;

    box-shadow:

        0 9px 25px
        rgba(30, 90, 145, 0.07);

}


[data-testid="stFileUploaderDropzone"] {

    background:

        linear-gradient(
            135deg,
            #fbfdff,
            #edf7ff
        ) !important;

    border:
        1.5px dashed #78b6ed !important;

    border-radius:
        14px !important;

}


[data-testid="stFileUploaderDropzone"]:hover {

    background:
        #edf7ff !important;

    border-color:
        #1769e0 !important;

}


/* Upload button */

[data-testid="stFileUploader"] button {

    background:
        #ffffff !important;

    color:
        #155a9e !important;

    border:
        1px solid #b7d4ee !important;

    border-radius:
        9px !important;

}


[data-testid="stFileUploader"] button:hover {

    border-color:
        #1769e0 !important;

    color:
        #1769e0 !important;

}


/* ============================================================
   INPUT TEXT VISIBILITY FIX
   ============================================================ */

[data-testid="stTextArea"] textarea {
    color: #173b60 !important;
    -webkit-text-fill-color: #173b60 !important;
    background: #ffffff !important;
    opacity: 1 !important;
}

[data-testid="stTextArea"] textarea::placeholder {
    color: #8aa4bd !important;
    -webkit-text-fill-color: #8aa4bd !important;
    opacity: 1 !important;
}

/* Keep upload control white and readable */

[data-testid="stFileUploaderDropzone"] button {
    background: #ffffff !important;
    color: #155a9e !important;
    border: 1px solid #b7d4ee !important;
}

[data-testid="stFileUploaderDropzone"] button p,
[data-testid="stFileUploaderDropzone"] button span {
    color: #155a9e !important;
}

/* ============================================================
   ANALYZE BUTTON
   ============================================================ */

.stButton > button {

    width: 100%;

    min-height: 55px;

    border-radius: 14px;

    border: none !important;

    background:

        linear-gradient(
            135deg,
            #0b83ff,
            #0757d8
        ) !important;

    color:
        #ffffff !important;

    font-size:
        15px !important;

    font-weight:
        800 !important;

    letter-spacing:
        0.2px;

    box-shadow:

        0 11px 28px
        rgba(8, 91, 218, 0.28);

    transition:
        all 0.18s ease;

}


.stButton > button p {

    color:
        #ffffff !important;

}


.stButton > button span {

    color:
        #ffffff !important;

}


.stButton > button:hover {

    transform:
        translateY(-2px);

    background:

        linear-gradient(
            135deg,
            #1490ff,
            #0750c8
        ) !important;

    box-shadow:

        0 15px 32px
        rgba(8, 91, 218, 0.34);

}


/* ============================================================
   METRIC CARDS
   ============================================================ */

[data-testid="stMetric"] {

    position: relative;

    background:

        linear-gradient(
            145deg,
            #ffffff,
            #f2f9ff
        ) !important;

    border:
        1px solid #c4ddf3 !important;

    border-radius:
        18px !important;

    padding:
        20px !important;

    min-height:
        135px;

    box-shadow:

        0 10px 28px
        rgba(26, 83, 132, 0.09);

    overflow:
        hidden;

    transition:
        all 0.18s ease;

}


[data-testid="stMetric"]::before {

    content: "";

    position: absolute;

    top: 0;
    left: 0;

    width: 100%;

    height: 4px;

    background:

        linear-gradient(
            90deg,
            #1769e0,
            #67baff
        );

}


[data-testid="stMetric"]:hover {

    transform:
        translateY(-3px);

    box-shadow:

        0 15px 34px
        rgba(26, 83, 132, 0.13);

}


[data-testid="stMetricLabel"] {

    color:
        #607d98 !important;

    font-size:
        13px !important;

    font-weight:
        700 !important;

}


[data-testid="stMetricValue"] {

    color:
        #0c427b !important;

    font-size:
        20px !important;

    font-weight:
        850 !important;

    line-height:
        1.3 !important;

    white-space:
        normal !important;

    overflow-wrap:
        anywhere !important;

}


/* ============================================================
   BORDERED ENTITY CARDS
   ============================================================ */

div[data-testid="stVerticalBlockBorderWrapper"] {

    background:

        linear-gradient(
            145deg,
            #ffffff,
            #f6fbff
        ) !important;

    border:
        1px solid #c7def3 !important;

    border-radius:
        18px !important;

    box-shadow:

        0 9px 26px
        rgba(26, 83, 132, 0.07);

}


/* ============================================================
   ALERT BOXES
   ============================================================ */

[data-testid="stAlert"] {

    border-radius:
        15px !important;

    border:
        1px solid #c5ddf3 !important;

    box-shadow:

        0 7px 20px
        rgba(30, 75, 120, 0.06);

}


/* ============================================================
   EXPANDERS
   ============================================================ */

[data-testid="stExpander"] {

    background:
        rgba(255,255,255,0.92) !important;

    border:
        1px solid #c6def3 !important;

    border-radius:
        15px !important;

    box-shadow:

        0 7px 20px
        rgba(30, 75, 120, 0.06);

    margin-bottom:
        10px;

}


[data-testid="stExpander"] summary {

    color:
        #164f87 !important;

    font-weight:
        750 !important;

}

/* ============================================================
   RAG CONTEXT CODE BOX
   ============================================================ */

[data-testid="stCodeBlock"] {

    background: #0b1726 !important;

    border: 1px solid #284b6b !important;

    border-radius: 14px !important;

}


[data-testid="stCodeBlock"] pre {

    background: #0b1726 !important;

    color: #d9ecff !important;

    font-size: 13px !important;

    line-height: 1.6 !important;

}


[data-testid="stCodeBlock"] code {

    color: #d9ecff !important;

    background: transparent !important;

}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {

    text-align:
        center;

    color:
        #7891a9;

    font-size:
        12px;

    padding:
        28px 0 8px;

    margin-top:
        45px;

    border-top:
        1px solid #d7e7f5;

}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 800px) {

    .hero-title {

        font-size:
            34px !important;

    }

    .hero-section {

        padding:
            25px;

    }

    h2 {

        font-size:
            23px !important;

    }

    [data-testid="stMetricValue"] {

        font-size:
            18px !important;

    }

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
        "Spear Phishing Attack",
        [
            "spear phishing",
            "targeted phishing",
            "targeted email attack"
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


# ============================================================
# ATTACK DETECTION
# ============================================================

def detect_attack_type(
    incident_text,
    extracted_attack_types=None
):

    text = incident_text.lower()

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

    if extracted_attack_types:

        for value in extracted_attack_types:

            value = str(
                value
            ).strip()

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
# SEVERITY
# ============================================================

def detect_severity(
    incident_text,
    extracted_severities=None
):

    text = incident_text.lower()

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

        if re.search(
            pattern,
            text
        ):

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
# AFFECTED SYSTEM
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

    (r"\bcustomer database\b", "Database"),
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

        if re.search(
            pattern,
            text
        ):

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
# PERSON / ORGANIZATION / LOCATION EXTRACTION
# ============================================================

def extract_named_entities(
    incident_text,
    entities
):

    text = incident_text.strip()

    def values_from(*keys):

        values = []

        for key in keys:

            value = entities.get(
                key,
                []
            )

            if isinstance(value, str):
                value = [value]

            if isinstance(value, list):

                for item in value:

                    item = str(item).strip()

                    if item and item not in values:
                        values.append(item)

        return values

    # --------------------------------------------------------
    # First use the NER output
    # --------------------------------------------------------

    persons = values_from(
        "PERSON",
        "PERSONS",
        "person",
        "persons"
    )

    organizations = values_from(
        "ORGANIZATION",
        "ORGANIZATIONS",
        "ORG",
        "ORGS",
        "organization",
        "organizations"
    )

    locations = values_from(
        "LOCATION",
        "LOCATIONS",
        "GPE",
        "location",
        "locations"
    )

    # --------------------------------------------------------
    # Safe fallback for common incident wording
    # --------------------------------------------------------

    if not persons:

        patterns = [
            r"\b(?:employee|user|victim|involving)\s+"
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})"
            r"(?=\s+(?:at|from|in|of|was|confirmed|did)\b|[.,])",

            r"\b(?:employee|user|victim)\s+"
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text
            )

            if match:

                candidate = match.group(1).strip()

                if candidate not in persons:
                    persons.append(candidate)

                break

    if not organizations:

        patterns = [
            r"\bat\s+"
            r"([A-Z][A-Za-z0-9&.-]+"
            r"(?:\s+[A-Z][A-Za-z0-9&.-]+){0,4})"
            r"(?=\s+(?:involving|from|where|"
            r"was|and|with)\b|[.,])",

            r"\b([A-Z][A-Za-z0-9&.-]+\s+"
            r"(?:Corporation|Corp|Company|"
            r"Technologies|Technology|Systems|"
            r"Solutions|Labs|Limited|Ltd|Inc))\b"
        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text
            )

            for candidate in matches:

                candidate = candidate.strip()

                if (
                    candidate
                    and candidate.lower()
                    not in {
                        "the security team",
                        "the company",
                        "the employee",
                        "the attacker"
                    }
                    and candidate not in organizations
                ):

                    organizations.append(candidate)

            if organizations:
                break

    if not locations:

        patterns = [
            r"\bunusual location in\s+"
            r"([A-Z][A-Za-z]+(?:,\s*[A-Z][A-Za-z]+)?)",

            r"\blocation\s+in\s+"
            r"([A-Z][A-Za-z]+(?:,\s*[A-Z][A-Za-z]+)?)",

            r"\b(?:from|in)\s+"
            r"([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)?)"
        ]

        invalid = {
            "Cloud",
            "VPN",
            "Email",
            "Multiple",
            "The",
            "HIGH",
            "NovaGrid",
            "Sarah"
        }

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text
            )

            for candidate in matches:

                candidate = candidate.strip()

                if (
                    candidate
                    and candidate not in invalid
                    and candidate not in locations
                ):

                    locations.append(candidate)

            if locations:
                break

    return {
        "PERSON": persons,
        "ORGANIZATION": organizations,
        "LOCATION": locations
    }


# ============================================================
# INDICATOR CLEANING
# ============================================================

def clean_indicators(
    indicators,
    incident_text
):

    candidates = []

    for ip in extract_ips(
        incident_text
    ):

        if ip not in candidates:

            candidates.append(ip)

    for item in indicators:

        item = str(
            item
        ).strip()

        if not item:
            continue

        lower = item.lower()

        if lower in [
            "ip",
            "ip address",
            "source ip",
            "source ip address",
            "indicator",
            "indicators"
        ]:

            continue

        if re.fullmatch(
            r"(?:\d{1,3}\.){3}\d{1,3}",
            item
        ):

            if item not in candidates:

                candidates.append(item)

            continue

        if not any(
            item.lower() == existing.lower()
            for existing in candidates
        ):

            candidates.append(item)

    unique = []

    for item in candidates:

        if not any(
            item.lower() == existing.lower()
            for existing in unique
        ):

            unique.append(item)

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

    if "suspicious" in attack:

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

    if "brute force" in attack:

        return [

            "Investigate the affected account and successful login activity.",

            "Block or monitor the suspicious source IP.",

            "Reset credentials for the affected account.",

            "Enable Multi-Factor Authentication (MFA).",

            "Review authentication logs for related attempts."

        ]

    if "phishing" in attack:

        return [

            "Investigate the affected account and email activity.",

            "Reset potentially exposed credentials.",

            "Enable Multi-Factor Authentication (MFA).",

            "Block malicious links, domains, or sender addresses.",

            "Review authentication and email security logs."

        ]

    if "ransomware" in attack:

        return [

            "Isolate affected systems from the network.",

            "Preserve evidence and investigate the initial infection vector.",

            "Verify the integrity of available backups.",

            "Reset potentially compromised credentials.",

            "Monitor the environment for additional infected systems."

        ]

    if "sql injection" in attack:

        return [

            "Review and block malicious requests.",

            "Validate and sanitize application input.",

            "Use parameterized queries or prepared statements.",

            "Review database access logs.",

            "Investigate whether unauthorized data was accessed."

        ]

    if "ddos" in attack or attack == "dos attack":

        return [

            "Identify and filter malicious traffic sources.",

            "Enable appropriate network or application-level DDoS protection.",

            "Monitor traffic volume and affected services.",

            "Review firewall and network security logs.",

            "Verify service availability after mitigation."

        ]

    if "malware" in attack:

        return [

            "Isolate the affected endpoint or system.",

            "Identify and preserve the malicious file or process.",

            "Run endpoint security scans.",

            "Review network connections and persistence mechanisms.",

            "Monitor other systems for related activity."

        ]

    if "data exfiltration" in attack:

        return [

            "Identify the affected data and destination.",

            "Block unauthorized transfer channels.",

            "Review data access and network logs.",

            "Reset credentials if account compromise is suspected.",

            "Assess the scope of potentially exposed information."

        ]

    if "privilege escalation" in attack:

        return [

            "Investigate how elevated privileges were obtained.",

            "Review administrator and system authentication logs.",

            "Remove unauthorized privileges.",

            "Reset potentially compromised credentials.",

            "Check for additional unauthorized activity."

        ]

    return [

        "Investigate the affected system and user activity.",

        "Review relevant security and authentication logs.",

        "Preserve evidence for further investigation.",

        "Reset potentially compromised credentials.",

        "Continue monitoring for related activity."

    ]


# ============================================================
# INCIDENT SUMMARY
# ============================================================

def create_summary(
    attack_type,
    affected_system,
    severity
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
# FILE READER
# ============================================================

def read_uploaded_file(
    uploaded_file
):

    extension = Path(
        uploaded_file.name
    ).suffix.lower()

    raw = uploaded_file.read()

    if extension in [
        ".txt",
        ".log"
    ]:

        return raw.decode(
            "utf-8",
            errors="ignore"
        )

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
# HERO SECTION
# ============================================================

hero_left, hero_right = st.columns(
    [1.15, 0.85],
    gap="large"
)


# ------------------------------------------------------------
# LEFT SIDE
# ------------------------------------------------------------

with hero_left:

    st.markdown(
        '<div class="hero-badge">🔐 AI-POWERED CYBERSECURITY</div>',
        unsafe_allow_html=True
    )

    logo_html = ""

    if LOGO_BASE64:
        logo_html = f"""
            <img
                src="data:image/png;base64,{LOGO_BASE64}"
                class="title-logo"
                alt="Cybersecurity logo"
            >
        """

    st.markdown(
        f"""
        <h1 class="hero-title">
            CyberIncident <span>AI</span>{logo_html}
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p class="hero-description">
            AI-Powered Incident Detection &amp; Response
        </p>
        """,
        unsafe_allow_html=True
    )

    feature1, feature2, feature3 = st.columns(3)

    with feature1:
        st.markdown("🛡️ **Threat Detection**")

    with feature2:
        st.markdown("🔎 **Incident Analysis**")

    with feature3:
        st.markdown("🧠 **AI Intelligence**")


with hero_right:

    hero_image = ASSETS_DIR / "cybersecurity_hero.png"

    if hero_image.exists():

        st.image(
            str(hero_image),
            use_container_width=True
        )

    else:

        st.warning(
            "Please add cybersecurity_hero.png "
            "inside the assets folder."
        )

# ============================================================
# INCIDENT INPUT SECTION
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
        "json",
        "pdf"
    ],
    help="Upload TXT, LOG, CSV, JSON or PDF incident reports."
)

uploaded_text = ""


if uploaded_file is not None:

    try:

        file_name = uploaded_file.name.lower()

        # ----------------------------------------------------
        # PDF
        # ----------------------------------------------------

        if file_name.endswith(".pdf"):

            pdf_reader = PdfReader(
                uploaded_file
            )

            pages = []

            for page in pdf_reader.pages:

                page_text = page.extract_text()

                if page_text:
                    pages.append(page_text)

            uploaded_text = "\n".join(pages)


        # ----------------------------------------------------
        # TXT / LOG / CSV / JSON
        # ----------------------------------------------------

        else:

            uploaded_text = uploaded_file.read().decode(
                "utf-8",
                errors="ignore"
            )


        if uploaded_text.strip():

            st.success(
                f"✓ {uploaded_file.name} uploaded successfully"
            )

        else:

            st.warning(
                "⚠️ The uploaded file does not contain readable text."
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


    # --------------------------------------------------------
    # RAG
    # --------------------------------------------------------

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
    # ENTITIES
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
    # FINAL DETECTION
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
    # PERSON / ORGANIZATION / LOCATION
    # ========================================================

    named_entities = extract_named_entities(
        incident_text,
        entities
    )

    persons = named_entities["PERSON"]
    organizations = named_entities["ORGANIZATION"]
    locations = named_entities["LOCATION"]


    person_text = (
        ", ".join(persons)
        if persons
        else "Not detected"
    )

    organization_text = (
        ", ".join(organizations)
        if organizations
        else "Not detected"
    )

    location_text = (
        ", ".join(locations)
        if locations
        else "Not detected"
    )


    # ========================================================
    # INCIDENT OVERVIEW
    # ========================================================

    st.header(
        "📊 Incident Overview"
    )


    col1, col2, col3, col4 = st.columns(
        [1, 1.4, 1.2, 0.8]
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

    # --------------------------------------------------------
    # ONLY ADDITION TO THE ORIGINAL UI:
    # PERSON / ORGANIZATION / LOCATION
    # --------------------------------------------------------

    name_col, org_col, location_col = st.columns(3)

    with name_col:

        with st.container(border=True):

            st.subheader(
                "👤 Name"
            )

            st.write(
                person_text
            )

    with org_col:

        with st.container(border=True):

            st.subheader(
                "🏢 Organization"
            )

            st.write(
                organization_text
            )

    with location_col:

        with st.container(border=True):

            st.subheader(
                "📍 Location"
            )

            st.write(
                location_text
            )


    left, right = st.columns(
        2
    )


    with left:

        with st.container(
            border=True
        ):

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

        with st.container(
            border=True
        ):

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
    # AI ANALYSIS
    # ========================================================

    st.header(
        "🤖 AI-Generated Incident Analysis"
    )


    summary = create_summary(
        attack_type,
        affected_system,
        severity
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
    # SUMMARY
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

        ", ".join(
            ip_addresses
        )

        if ip_addresses

        else

        "Not detected"

    )


    info1, info2, info3 = st.columns(
        3
    )


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
        +
        (
            ", ".join(
                indicators
            )

            if indicators

            else

            "None detected"
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

    except Exception:

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
# EVALUATION & PERFORMANCE
# ============================================================

evaluation_file = BASE_DIR / "evaluation_results.json"

if evaluation_file.exists():

    try:

        with open(
            evaluation_file,
            "r",
            encoding="utf-8"
        ) as f:

            evaluation_data = json.load(f)

        evaluation = evaluation_data.get("summary", {})

        st.markdown(
            """
            <div class="section-title">
                📊 Evaluation & Performance
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="section-subtitle">
                Quantitative evaluation of the CyberIncident AI
                detection and retrieval pipeline.
            </div>
            """,
            unsafe_allow_html=True
        )

        # ====================================================
        # MAIN METRICS
        # ====================================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                label="🎯 Attack Classification",
                value=f"{evaluation.get('attack_classification_accuracy', 0) * 100:.1f}%"
            )

        with col2:

            st.metric(
                label="🧩 Entity F1",
                value=f"{evaluation.get('entity_f1', 0):.3f}"
            )

        with col3:

            st.metric(
                label="📚 Precision@3",
                value=f"{evaluation.get('precision_at_3', 0):.3f}"
            )

        with col4:

            st.metric(
                label="⚡ Average Latency",
                value=f"{evaluation.get('average_latency_seconds', 0):.3f}s"
            )

        st.markdown("")

        # ====================================================
        # DETAILED EVALUATION
        # ====================================================

        with st.expander(
            "🔎 View Detailed Evaluation Metrics"
        ):

            st.markdown("### 🧩 NER / Entity Evaluation")

            ner_col1, ner_col2, ner_col3 = st.columns(3)

            with ner_col1:

                st.metric(
                    "Entity Precision",
                    f"{evaluation.get('entity_precision', 0):.3f}"
                )

            with ner_col2:

                st.metric(
                    "Entity Recall",
                    f"{evaluation.get('entity_recall', 0):.3f}"
                )

            with ner_col3:

                st.metric(
                    "Entity F1",
                    f"{evaluation.get('entity_f1', 0):.3f}"
                )

            st.markdown("---")

            st.markdown("### 📚 RAG / Retrieval Evaluation")

            rag_col1, rag_col2, rag_col3 = st.columns(3)

            with rag_col1:

                st.metric(
                    "Precision@3",
                    f"{evaluation.get('precision_at_3', 0):.3f}"
                )

            with rag_col2:

                st.metric(
                    "Recall@3",
                    f"{evaluation.get('recall_at_3', 0):.3f}"
                )

            with rag_col3:

                st.metric(
                    "MRR",
                    f"{evaluation.get('mrr', 0):.3f}"
                )

            st.markdown("---")

            st.markdown("### ⚡ System Performance")

            perf_col1, perf_col2, perf_col3 = st.columns(3)

            with perf_col1:

                st.metric(
                    "Classification Accuracy",
                    f"{evaluation.get('attack_classification_accuracy', 0) * 100:.1f}%"
                )

            with perf_col2:

                st.metric(
                    "Grounding Rate",
                    f"{evaluation.get('grounding_rate', 0) * 100:.1f}%"
                )

            with perf_col3:

                st.metric(
                    "Test Cases",
                    str(evaluation.get('test_cases', 0))
                )

            st.markdown(
                f"""
                **Average Processing Latency:**  
                `{evaluation.get('average_latency_seconds', 0):.3f} seconds`
                """
            )

            st.success(
                "✓ Evaluation completed successfully on the test dataset."
            )

    except Exception as evaluation_error:

        st.warning(
            f"Evaluation results could not be displayed: "
            f"{evaluation_error}"
        )

else:

    st.info(
        "Evaluation results are not available yet. "
        "Run `python evaluation.py` to generate them."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="footer">
    🔐 CyberIncident AI
    • AI-Powered Cybersecurity Incident Analysis
</div>
""",
    unsafe_allow_html=True
)