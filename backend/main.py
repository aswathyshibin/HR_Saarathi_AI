# =========================================================
# HR SAARATHI AI
# MAIN FASTAPI APPLICATION
# =========================================================

import uuid
import traceback
import sys

from pathlib import Path

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from fastapi.staticfiles import (
    StaticFiles
)

from fastapi.responses import (
    FileResponse
)

from pydantic import BaseModel


# Keep Unicode transcripts from crashing the app on Windows consoles
# that cannot encode them using their active code page.
for stream in (sys.stdout, sys.stderr):

    if hasattr(stream, "reconfigure"):

        stream.reconfigure(
            errors="backslashreplace"
        )


# =========================================================
# SERVICES
# =========================================================

from .config import validate_config

from .groq_service import (
    transcribe_audio,
    understand_question,
    generate_answer
)

from .sheets_service import (
    get_attendance_dataframe,
    get_employee_names
)

from .attendance_service import (
    analyze_attendance
)

from .conversation_service import (
    conversation_manager
)


# =========================================================
# APP
# =========================================================

app = FastAPI(

    title="HR Saarathi AI",

    description=(
        "Malayalam-English Voice HR Attendance Assistant"
    ),

    version="1.0.0"

)


# =========================================================
# CORS
# =========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)


# =========================================================
# CONFIGURATION
# =========================================================

try:

    validate_config()

    print()
    print("=" * 70)
    print("HR SAARATHI CONFIGURATION")
    print("=" * 70)
    print("Configuration loaded successfully.")
    print("=" * 70)


except Exception as e:

    print()
    print("=" * 70)
    print("CONFIGURATION WARNING")
    print("=" * 70)

    print(str(e))

    print("=" * 70)


# =========================================================
# FRONTEND
# =========================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

FRONTEND_DIR = (
    BASE_DIR / "frontend"
)


# =========================================================
# REQUEST MODEL
# =========================================================

class TextQuestion(BaseModel):

    question: str

    session_id: str | None = None


# =========================================================
# HOME
# =========================================================

@app.get("/")
async def home():

    return FileResponse(

        FRONTEND_DIR / "index.html"

    )


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
async def health():

    return {

        "status": "ok",

        "service": "HR Saarathi AI"

    }


# =========================================================
# EMPLOYEES
# =========================================================

@app.get("/employees")
async def employees():

    try:

        names = get_employee_names()

        return {

            "employees": names

        }

    except Exception as e:

        print()
        print("EMPLOYEE ERROR:")
        print(repr(e))

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# =========================================================
# TEXT QUESTION
# =========================================================

@app.post("/ask")
async def ask_question(

    request: TextQuestion

):

    # -----------------------------------------------------
    # Validate question
    # -----------------------------------------------------

    if not request.question.strip():

        raise HTTPException(

            status_code=400,

            detail="Question cannot be empty."

        )


    # -----------------------------------------------------
    # Session
    # -----------------------------------------------------

    session_id = (

        request.session_id

        or str(uuid.uuid4())

    )


    print()
    print("=" * 70)
    print("TEXT QUESTION")
    print("=" * 70)

    print(
        "Question:",
        request.question
    )

    print(
        "Session:",
        session_id
    )


    try:

        # =================================================
        # GET CONVERSATION
        # =================================================

        conversation = (

            conversation_manager

            .get_messages(

                session_id

            )

        )


        # =================================================
        # UNDERSTAND QUESTION
        # =================================================

        print()
        print("STEP 1: Understanding question...")


        query = understand_question(

            request.question,

            conversation

        )


        print()
        print("INTERPRETED QUERY:")
        print(query)


        # =================================================
        # GET ATTENDANCE DATA
        # =================================================

        print()
        print("STEP 2: Getting attendance data...")


        df = get_attendance_dataframe()


        print(
            "Records received:",
            len(df)
        )


        # =================================================
        # EMPTY DATA
        # =================================================

        if df.empty:

            answer = (

                "No attendance data is "
                "currently available."

            )


            return {

                "success": True,

                "session_id":
                    session_id,

                "question":
                    request.question,

                "answer":
                    answer,

                "query":
                    query,

                "result":
                    {}

            }


        # =================================================
        # ANALYZE ATTENDANCE
        # =================================================

        print()
        print("STEP 3: Analyzing attendance data...")


        result = analyze_attendance(

            df,

            query

        )


        print()
        print("ATTENDANCE RESULT:")
        print(result)


        # =================================================
        # GENERATE ANSWER
        # =================================================

        print()
        print("STEP 4: Generating HR answer...")


        answer = generate_answer(

            request.question,

            query,

            result,

            conversation

        )


        print()
        print("HR SAARATHI ANSWER:")
        print(answer)


        # =================================================
        # SAVE CONVERSATION
        # =================================================

        conversation_manager.add_message(

            session_id,

            "user",

            request.question

        )


        conversation_manager.add_message(

            session_id,

            "assistant",

            answer

        )


        # =================================================
        # RETURN
        # =================================================

        return {

            "success": True,

            "session_id":
                session_id,

            "question":
                request.question,

            "answer":
                answer,

            "query":
                query,

            "result":
                result

        }


    except HTTPException:

        raise


    except Exception as e:

        print()
        print("=" * 70)
        print("TEXT PROCESSING ERROR")
        print("=" * 70)

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )

        traceback.print_exc()


        raise HTTPException(

            status_code=500,

            detail=(

                "Unable to process "
                "your question: "

                + str(e)

            )

        )


# =========================================================
# VOICE QUESTION
# =========================================================

@app.post("/ask-voice")
async def ask_voice(

    audio: UploadFile = File(...),

    session_id: str | None = None

):

    print()
    print("=" * 70)
    print("VOICE API REQUEST RECEIVED")
    print("=" * 70)


    # =====================================================
    # VALIDATE AUDIO
    # =====================================================

    if audio is None:

        raise HTTPException(

            status_code=400,

            detail="Audio file is missing."

        )


    if not audio.filename:

        raise HTTPException(

            status_code=400,

            detail="Audio filename is missing."

        )


    print(
        "Filename:",
        audio.filename
    )

    print(
        "Content-Type:",
        audio.content_type
    )


    # =====================================================
    # SESSION
    # =====================================================

    session_id = (

        session_id

        or str(uuid.uuid4())

    )


    print(
        "Session ID:",
        session_id
    )


    try:

        # =================================================
        # GET CONVERSATION
        # =================================================

        conversation = (

            conversation_manager

            .get_messages(

                session_id

            )

        )


        print()
        print(
            "Conversation messages:",
            len(conversation)
        )


        # =================================================
        # STEP 1
        # SPEECH → TEXT
        # =================================================

        print()
        print("=" * 70)
        print("STEP 1: SPEECH → TEXT")
        print("=" * 70)


        question = transcribe_audio(

            audio

        )


        print()
        print("TRANSCRIBED QUESTION:")
        print(question)


        # =================================================
        # CHECK TRANSCRIPTION
        # =================================================

        if question is None:

            raise HTTPException(

                status_code=400,

                detail=(
                    "Could not understand "
                    "the audio."
                )

            )


        question = str(
            question
        ).strip()


        if not question:

            raise HTTPException(

                status_code=400,

                detail=(
                    "Could not understand "
                    "the audio."
                )

            )


        # =================================================
        # STEP 2
        # UNDERSTAND QUESTION
        # =================================================

        print()
        print("=" * 70)
        print("STEP 2: UNDERSTANDING VOICE QUESTION")
        print("=" * 70)


        query = understand_question(

            question,

            conversation

        )


        print()
        print("INTERPRETED QUERY:")
        print(query)


        # =================================================
        # STEP 3
        # GET ATTENDANCE DATA
        # =================================================

        print()
        print("=" * 70)
        print("STEP 3: GETTING ATTENDANCE DATA")
        print("=" * 70)


        df = get_attendance_dataframe()


        print(
            "Records received:",
            len(df)
        )


        # =================================================
        # EMPTY DATA
        # =================================================

        if df.empty:

            answer = (

                "No attendance data is "
                "currently available."

            )


            conversation_manager.add_message(

                session_id,

                "user",

                question

            )


            conversation_manager.add_message(

                session_id,

                "assistant",

                answer

            )


            return {

                "success": True,

                "session_id":
                    session_id,

                "transcription":
                    question,

                "question":
                    question,

                "answer":
                    answer,

                "query":
                    query,

                "result":
                    {}

            }


        # =================================================
        # STEP 4
        # ANALYZE ATTENDANCE
        # =================================================

        print()
        print("=" * 70)
        print("STEP 4: ANALYZING ATTENDANCE")
        print("=" * 70)


        result = analyze_attendance(

            df,

            query

        )


        print()
        print("ATTENDANCE RESULT:")
        print(result)


        # =================================================
        # STEP 5
        # GENERATE ANSWER
        # =================================================

        print()
        print("=" * 70)
        print("STEP 5: GENERATING HR ANSWER")
        print("=" * 70)


        answer = generate_answer(

            question,

            query,

            result,

            conversation

        )


        print()
        print("HR SAARATHI ANSWER:")
        print(answer)


        # =================================================
        # CHECK ANSWER
        # =================================================

        if answer is None:

            raise HTTPException(

                status_code=500,

                detail=(
                    "Question was transcribed, "
                    "but HR Saarathi could not "
                    "generate an answer."
                )

            )


        answer = str(
            answer
        ).strip()


        if not answer:

            raise HTTPException(

                status_code=500,

                detail=(
                    "Question was transcribed, "
                    "but HR Saarathi returned "
                    "an empty answer."
                )

            )


        # =================================================
        # SAVE CONVERSATION
        # =================================================

        print()
        print("Saving voice conversation...")


        conversation_manager.add_message(

            session_id,

            "user",

            question

        )


        conversation_manager.add_message(

            session_id,

            "assistant",

            answer

        )


        # =================================================
        # SUCCESS RESPONSE
        # =================================================

        print()
        print("=" * 70)
        print("VOICE API SUCCESS")
        print("=" * 70)

        print(
            "Question:",
            question
        )

        print(
            "Answer:",
            answer
        )


        return {

            "success": True,

            "session_id":
                session_id,

            "transcription":
                question,

            "question":
                question,

            "answer":
                answer,

            "query":
                query,

            "result":
                result

        }


    except HTTPException:

        raise


    except Exception as e:

        print()
        print("=" * 70)
        print("VOICE API ERROR")
        print("=" * 70)

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )

        traceback.print_exc()


        raise HTTPException(

            status_code=500,

            detail=(

                "Voice processing failed: "

                + str(e)

            )

        )


# =========================================================
# CLEAR CONVERSATION
# =========================================================

@app.delete(
    "/conversation/{session_id}"
)
async def clear_conversation(

    session_id: str

):

    conversation_manager.clear(

        session_id

    )


    return {

        "message":
            "Conversation cleared."

    }


# =========================================================
# STATIC FILES
# =========================================================

app.mount(

    "/static",

    StaticFiles(

        directory=FRONTEND_DIR

    ),

    name="static"

)