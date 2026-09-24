import pandas as pd
import re
from pathlib import Path


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

INCIDENT_FILE = BASE_DIR / "data" / "knowledge_base" / "incidents.csv"
GUIDANCE_FILE = BASE_DIR / "data" / "knowledge_base" / "cybersecurity_guidance.txt"

OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def clean_text(text):
    """Clean and normalize text."""

    if pd.isna(text):
        return ""

    text = str(text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing spaces
    text = text.strip()

    return text


def preprocess_incidents():
    """Load and clean the incident dataset."""

    df = pd.read_csv(INCIDENT_FILE)

    print(f"Original incident records: {len(df)}")

    # Remove duplicate incident records
    df = df.drop_duplicates(subset=["incident_id"])

    # Clean text columns
    text_columns = [
        "attack_type",
        "affected_system",
        "severity",
        "indicators",
        "description",
        "response_taken",
        "attack_techniques",
        "source_type"
    ]

    for column in text_columns:
        df[column] = df[column].apply(clean_text)

    # Fill missing values
    df[text_columns] = df[text_columns].fillna("Unknown")

    # Remove records without an incident ID
    df = df[df["incident_id"].str.strip() != ""]

    # Create a combined text field for later NLP/RAG processing
    df["combined_text"] = (
        "Incident ID: " + df["incident_id"] +
        "\nAttack Type: " + df["attack_type"] +
        "\nAffected System: " + df["affected_system"] +
        "\nSeverity: " + df["severity"] +
        "\nIndicators: " + df["indicators"] +
        "\nDescription: " + df["description"] +
        "\nResponse Taken: " + df["response_taken"] +
        "\nAttack Techniques: " + df["attack_techniques"]
    )

    output_file = OUTPUT_DIR / "cleaned_incidents.csv"
    df.to_csv(output_file, index=False)

    print(f"Cleaned incident records: {len(df)}")
    print(f"Saved to: {output_file}")

    return df


def preprocess_guidance():
    """Load and clean cybersecurity guidance."""

    with open(GUIDANCE_FILE, "r", encoding="utf-8") as file:
        text = file.read()

    text = clean_text(text)

    output_file = OUTPUT_DIR / "cleaned_guidance.txt"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(text)

    print(f"Guidance characters: {len(text)}")
    print(f"Saved to: {output_file}")

    return text


if __name__ == "__main__":

    print("=" * 60)
    print("CYBERINCIDENT AI - DATA PREPROCESSING")
    print("=" * 60)

    preprocess_incidents()
    preprocess_guidance()

    print("\nPreprocessing completed successfully!")