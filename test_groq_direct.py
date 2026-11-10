import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv(override=True)

api_key = os.getenv("GROQ_API_KEY")

print("=" * 60)
print("DIRECT GROQ API TEST")
print("=" * 60)

print()
print("Key found:", bool(api_key))
print("Prefix:", api_key[:4] if api_key else "NONE")
print("Length:", len(api_key) if api_key else 0)

if not api_key:
    raise SystemExit("GROQ_API_KEY not found")


client = Groq(
    api_key=api_key
)


try:

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "user",
                "content": "Say hello in one short sentence."
            }
        ],

        temperature=0

    )

    print()
    print("Response:")
    print(
        response.choices[0].message.content
    )

    print()
    print("=" * 60)
    print("GROQ API WORKING ✅")
    print("=" * 60)


except Exception as e:

    print()
    print("=" * 60)
    print("GROQ API FAILED ❌")
    print("=" * 60)

    print(
        type(e).__name__,
        ":",
        str(e)
    )