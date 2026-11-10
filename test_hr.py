from backend.hr_engine import ask_hr


print()
print("=" * 70)
print("HR SAARATHI - COMPLETE AI TEST")
print("=" * 70)


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
    print("-" * 70)

    print("QUESTION:")
    print(question)

    try:

        response = ask_hr(
            question
        )


        print()
        print("INTERPRETED QUERY:")

        print(
            response["query"]
        )


        print()
        print("VERIFIED ATTENDANCE RESULT:")

        print(
            response["result"]
        )


        print()
        print("HR SAARATHI ANSWER:")

        print(
            response["answer"]
        )


    except Exception as e:

        print()
        print("❌ ERROR:")

        print(
            type(e).__name__
            + ": "
            + str(e)
        )


print()
print("=" * 70)
print("COMPLETE HR AI TEST FINISHED")
print("=" * 70)