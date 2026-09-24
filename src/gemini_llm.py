import os

from google import genai
from google.genai import types

from rag import build_rag_context


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = "gemini-3.5-flash-lite"


if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(
        timeout=120000
    )
)


# ============================================================
# CREATE SHORT PROMPT
# ============================================================

def create_prompt(rag_result):

    incident = rag_result["incident"]
    entities = rag_result["entities"]

    # Use only top 2 retrieved knowledge sources
    retrieved = rag_result["retrieved_knowledge"][:2]

    # Format entities
    entity_lines = []

    for category, values in entities.items():

        if values:

            entity_lines.append(
                f"{category}: {', '.join(values)}"
            )

    entity_text = "\n".join(entity_lines)

    # Format retrieved knowledge
    knowledge_lines = []

    for index, result in enumerate(
        retrieved,
        start=1
    ):

        knowledge_lines.append(
            f"SOURCE {index}:\n{result['text']}"
        )

    knowledge_text = "\n\n".join(
        knowledge_lines
    )

    prompt = f"""
You are a cybersecurity incident analyst.

Analyze the incident using the supplied evidence
and retrieved cybersecurity knowledge.

Do not invent facts.

Return a concise report with exactly these sections:

1. INCIDENT SUMMARY
2. EXTRACTED INFORMATION
3. ATTACK TYPE
4. SEVERITY
5. SUSPICIOUS ACTIVITY
6. POSSIBLE IMPACT
7. RECOMMENDED ACTIONS
8. KNOWLEDGE SOURCES

Clearly distinguish reported facts from possible impact.
If information is unavailable, say "Not available".

INCIDENT:
{incident}

EXTRACTED ENTITIES:
{entity_text}

RETRIEVED KNOWLEDGE:
{knowledge_text}
"""

    return prompt


# ============================================================
# STREAM GEMINI ANALYSIS
# ============================================================

def generate_incident_analysis_stream(
    incident_text,
    rag_result=None
):

    # Avoid building RAG twice
    if rag_result is None:

        rag_result = build_rag_context(
            incident_text
        )

    prompt = create_prompt(
        rag_result
    )

    response_stream = client.models.generate_content_stream(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=600
        )
    )

    for chunk in response_stream:

        if chunk.text:

            yield chunk.text


# ============================================================
# NON-STREAMING VERSION
# ============================================================

def generate_incident_analysis(
    incident_text,
    rag_result=None
):

    output = ""

    for chunk in generate_incident_analysis_stream(
        incident_text,
        rag_result
    ):

        output += chunk

    return output


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CYBERINCIDENT AI - OPTIMIZED GEMINI TEST")
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

    try:

        rag_result = build_rag_context(
            test_incident
        )

        print("\nGenerating analysis...\n")

        for text in generate_incident_analysis_stream(
            test_incident,
            rag_result
        ):

            print(
                text,
                end="",
                flush=True
            )

        print("\n\n" + "=" * 60)
        print("OPTIMIZED GEMINI TEST COMPLETED")
        print("=" * 60)

    except Exception as error:

        print("\n❌ GEMINI ANALYSIS ERROR")
        print("=" * 60)
        print(type(error).__name__)
        print(str(error))
        print("=" * 60)