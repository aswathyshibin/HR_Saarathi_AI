from .sheets_service import (
    get_attendance_dataframe
)

from .groq_service import (
    understand_question,
    generate_answer
)

from .attendance_service import (
    process_attendance_query
)


# =========================================================
# HR SAARATHI MAIN ENGINE
# =========================================================

def ask_hr(
    question,
    conversation=None
):

    if conversation is None:
        conversation = []


    # =====================================================
    # STEP 1
    # GROQ UNDERSTANDS THE QUESTION
    # =====================================================

    print()
    print("STEP 1: Understanding question with Groq...")

    query = understand_question(
        question,
        conversation
    )

    print()
    print("Groq Query:")
    print(query)


    # =====================================================
    # STEP 2
    # GET LIVE GOOGLE SHEET DATA
    # =====================================================

    print()
    print("STEP 2: Getting attendance data...")

    df = get_attendance_dataframe()

    print(
        "Records received:",
        len(df)
    )


    # =====================================================
    # STEP 3
    # PYTHON ANALYZES DATA
    # =====================================================

    print()
    print("STEP 3: Analyzing attendance data...")

    result = process_attendance_query(
        df,
        query
    )

    print()
    print("Attendance Result:")
    print(result)


    # =====================================================
    # STEP 4
    # GROQ GENERATES FINAL ANSWER
    # =====================================================

    print()
    print("STEP 4: Generating HR answer...")

    answer = generate_answer(

        question,

        query,

        result,

        conversation

    )


    # =====================================================
    # RETURN FINAL RESPONSE
    # =====================================================

    return {

        "question":
            question,

        "query":
            query,

        "result":
            result,

        "answer":
            answer

    }