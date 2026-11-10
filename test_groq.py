from backend.groq_service import (
    understand_question
)


print()
print("=" * 60)
print("HR SAARATHI - GROQ QUESTION TEST")
print("=" * 60)


questions = [

    "Who took leave this month?",

    "ഈ മാസം ആരൊക്കെയാണ് leave എടുത്തത്?",

    "Who was absent yesterday?",

    "ഇന്ന് ആരൊക്കെയാണ് absent?",

    "What is Anil's attendance percentage?",

    "HR department-ൽ ആരൊക്കെയാണ് absent?"

]


for question in questions:

    print()
    print("-" * 60)

    print("QUESTION:")
    print(question)

    print()

    try:

        result = understand_question(
            question
        )

        print("GROQ RESULT:")

        print(result)

    except Exception as e:

        print()
        print("❌ ERROR")

        print(
            type(e).__name__
            + ": "
            + str(e)
        )


print()
print("=" * 60)
print("GROQ TEST FINISHED")
print("=" * 60)