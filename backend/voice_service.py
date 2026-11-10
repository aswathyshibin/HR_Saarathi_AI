# =========================================================
# HR SAARATHI - VOICE SERVICE
# =========================================================

import sys
from typing import Optional, Any

from .groq_service import transcribe_audio
from .hr_engine import ask_hr


for stream in (sys.stdout, sys.stderr):

    if hasattr(stream, "reconfigure"):

        stream.reconfigure(
            errors="backslashreplace"
        )


# =========================================================
# PROCESS VOICE QUESTION
# =========================================================

def process_voice_question(
    audio_file: Any,
    conversation: Optional[list] = None
):
    """
    Process a voice question for HR Saarathi.

    Flow:

        Audio
          ↓
        Groq Whisper
          ↓
        Text Question
          ↓
        HR Engine
          ↓
        Attendance Analysis
          ↓
        HR Answer
    """

    # -----------------------------------------------------
    # INITIALIZE CONVERSATION
    # -----------------------------------------------------

    if conversation is None:
        conversation = []


    print()
    print("=" * 70)
    print("              HR SAARATHI - VOICE PROCESSING")
    print("=" * 70)


    try:

        # =================================================
        # VALIDATE AUDIO
        # =================================================

        if audio_file is None:

            raise ValueError(
                "No audio file was provided."
            )


        # FastAPI UploadFile normally has filename
        filename = getattr(
            audio_file,
            "filename",
            None
        )


        content_type = getattr(
            audio_file,
            "content_type",
            None
        )


        print()
        print("AUDIO INFORMATION")
        print("-" * 70)

        print(
            "Filename:",
            filename
        )

        print(
            "Content type:",
            content_type
        )


        if filename is not None:

            if not filename.strip():

                raise ValueError(
                    "Audio filename is empty."
                )


        # =================================================
        # STEP 1
        # SPEECH → TEXT
        # =================================================

        print()
        print("=" * 70)
        print("STEP 1: SPEECH → TEXT")
        print("=" * 70)


        print(
            "Sending audio to Groq Whisper..."
        )


        try:

            question = transcribe_audio(
                audio_file
            )

        except Exception as error:

            print()
            print(
                "TRANSCRIPTION ERROR:"
            )

            print(
                type(error).__name__
            )

            print(
                str(error)
            )

            raise ValueError(
                "Speech transcription failed: "
                + str(error)
            )


        # =================================================
        # VALIDATE TRANSCRIPTION
        # =================================================

        if question is None:

            raise ValueError(
                "Groq returned no transcription."
            )


        question = str(
            question
        ).strip()


        if not question:

            raise ValueError(
                "Could not understand the audio."
            )


        print()
        print(
            "TRANSCRIBED QUESTION:"
        )

        print(
            question
        )


        # =================================================
        # STEP 2
        # SEND TEXT TO HR ENGINE
        # =================================================

        print()
        print("=" * 70)
        print("STEP 2: HR SAARATHI ENGINE")
        print("=" * 70)


        print(
            "Sending transcribed question to HR engine..."
        )


        try:

            response = ask_hr(

                question,

                conversation

            )

        except Exception as error:

            print()
            print(
                "HR ENGINE ERROR:"
            )

            print(
                type(error).__name__
            )

            print(
                str(error)
            )

            raise ValueError(
                "HR processing failed: "
                + str(error)
            )


        # =================================================
        # VALIDATE HR RESPONSE
        # =================================================

        if response is None:

            raise ValueError(
                "HR engine returned no response."
            )


        if not isinstance(
            response,
            dict
        ):

            raise ValueError(
                "Invalid response returned "
                "from HR engine."
            )


        print()
        print(
            "HR ENGINE RESPONSE RECEIVED"
        )


        # =================================================
        # EXTRACT RESPONSE
        # =================================================

        query = response.get(
            "query",
            {}
        )


        result = response.get(
            "result",
            {}
        )


        answer = response.get(
            "answer",
            ""
        )


        # =================================================
        # VALIDATE ANSWER
        # =================================================

        if answer is None:

            answer = ""


        answer = str(
            answer
        ).strip()


        # =================================================
        # DEBUG OUTPUT
        # =================================================

        print()
        print("-" * 70)

        print(
            "INTERPRETED QUERY:"
        )

        print(
            query
        )


        print()
        print(
            "ATTENDANCE RESULT:"
        )

        print(
            result
        )


        print()
        print(
            "HR SAARATHI ANSWER:"
        )

        print(
            answer
        )


        # =================================================
        # STEP 3
        # RETURN RESULT
        # =================================================

        print()
        print("=" * 70)
        print("VOICE PROCESSING SUCCESS")
        print("=" * 70)


        return {

            "success": True,

            "question": question,

            "query": query,

            "result": result,

            "answer": answer

        }


    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except ValueError as error:

        print()
        print("=" * 70)
        print("VOICE PROCESSING FAILED")
        print("=" * 70)

        print(
            "Error:",
            str(error)
        )


        return {

            "success": False,

            "question": "",

            "query": {},

            "result": {},

            "answer": "",

            "error": str(error)

        }


    except Exception as error:

        print()
        print("=" * 70)
        print("UNEXPECTED VOICE ERROR")
        print("=" * 70)


        print(
            "Error type:",
            type(error).__name__
        )

        print(
            "Error:",
            str(error)
        )


        import traceback

        traceback.print_exc()


        return {

            "success": False,

            "question": "",

            "query": {},

            "result": {},

            "answer": "",

            "error":
                "Unexpected voice processing error: "
                + str(error)

        }