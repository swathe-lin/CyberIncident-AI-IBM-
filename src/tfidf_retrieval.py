# ============================================================
# CYBERINCIDENT AI
# TF-IDF KNOWLEDGE RETRIEVAL
# ============================================================

import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# KNOWLEDGE BASE PATH
# ============================================================

KNOWLEDGE_BASE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "knowledge_base",
    "cybersecurity_guidance.txt"
)


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

def load_knowledge_base():
    """
    Load cybersecurity knowledge from the
    cybersecurity guidance text file.
    """

    if not os.path.exists(KNOWLEDGE_BASE_PATH):
        raise FileNotFoundError(
            f"Knowledge base not found at:\n"
            f"{KNOWLEDGE_BASE_PATH}"
        )

    with open(
        KNOWLEDGE_BASE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        content = file.read()

    return content


# ============================================================
# CREATE TEXT CHUNKS
# ============================================================

def create_chunks(text):
    """
    Split the knowledge base into separate
    paragraphs/chunks.
    """

    chunks = [
        chunk.strip()
        for chunk in text.split("\n\n")
        if chunk.strip()
    ]

    return chunks


# ============================================================
# TF-IDF RETRIEVAL
# ============================================================

def retrieve_relevant_knowledge(query, top_k=3):
    """
    Retrieve the most relevant knowledge-base
    chunks using TF-IDF and cosine similarity.
    """

    knowledge_text = load_knowledge_base()

    chunks = create_chunks(knowledge_text)

    if not chunks:
        return []

    # Query + knowledge chunks
    documents = [query] + chunks

    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(
        documents
    )

    # First vector is the query
    query_vector = tfidf_matrix[0]

    # Remaining vectors are knowledge chunks
    document_vectors = tfidf_matrix[1:]

    # Calculate similarity
    similarities = cosine_similarity(
        query_vector,
        document_vectors
    ).flatten()

    # Rank from highest similarity to lowest
    ranked_indices = similarities.argsort()[::-1]

    results = []

    for index in ranked_indices[:top_k]:

        results.append({
            "text": chunks[index],
            "score": float(similarities[index])
        })

    return results


# ============================================================
# TEST TF-IDF RETRIEVAL
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CYBERINCIDENT AI - TF-IDF RETRIEVAL TEST")
    print("=" * 60)

    test_query = """
    A phishing attack affected an email server.
    The attacker sent a suspicious login link
    that resulted in credential submission.
    The incident severity was high.
    """

    print("\nQUERY:")
    print(test_query.strip())

    print("\n" + "-" * 60)
    print("RETRIEVED KNOWLEDGE")
    print("-" * 60)

    results = retrieve_relevant_knowledge(
        test_query,
        top_k=3
    )

    if not results:

        print("No relevant knowledge found.")

    else:

        for i, result in enumerate(
            results,
            start=1
        ):

            print(f"\nRESULT {i}")

            print(
                f"Similarity Score: "
                f"{result['score']:.4f}"
            )

            print("Knowledge:")
            print(result["text"])

    print("\n" + "=" * 60)
    print("TF-IDF RETRIEVAL TEST COMPLETED")
    print("=" * 60)