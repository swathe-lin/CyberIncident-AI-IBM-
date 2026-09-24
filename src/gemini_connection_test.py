import os

from google import genai
from google.genai import types


API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set.")


client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(
        timeout=120000
    )
)


print("=" * 60)
print("GEMINI CONNECTION TEST")
print("=" * 60)

print("\nSending a very small request to Gemini...")

try:

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Reply with exactly: GEMINI CONNECTION SUCCESS"
    )

    print("\nGemini response:")
    print(response.text)

    print("\n" + "=" * 60)
    print("GEMINI CONNECTION TEST SUCCESSFUL")
    print("=" * 60)

except Exception as error:

    print("\n❌ GEMINI CONNECTION ERROR")
    print("=" * 60)
    print(type(error).__name__)
    print(str(error))
    print("=" * 60)