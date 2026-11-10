import os

from dotenv import load_dotenv


load_dotenv(
    override=True
)


print("=" * 60)
print("HR SAARATHI - ENVIRONMENT TEST")
print("=" * 60)


api_key = os.getenv(
    "GROQ_API_KEY"
)


if api_key:

    print()
    print("GROQ_API_KEY FOUND")

    print(
        "Prefix:",
        api_key[:4]
    )

    print(
        "Length:",
        len(api_key)
    )

else:

    print()
    print("GROQ_API_KEY NOT FOUND")


print()
print("=" * 60)