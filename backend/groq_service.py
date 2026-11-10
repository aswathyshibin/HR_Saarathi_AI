# =========================================================
# HR SAARATHI - GROQ SERVICE
# =========================================================

import json

from groq import Groq

from .config import (
    GROQ_API_KEY,
    GROQ_TEXT_MODEL,
    GROQ_STT_MODEL
)

from .prompts import (
    QUERY_SYSTEM_PROMPT,
    ANSWER_SYSTEM_PROMPT
)


# =========================================================
# GROQ CLIENT
# =========================================================

client = Groq(
    api_key=GROQ_API_KEY
)


# =========================================================
# SPEECH TO TEXT
# =========================================================

def transcribe_audio(audio_file):
    """
    Convert uploaded voice audio into text.

    Supported languages:
        - Malayalam
        - English

    IMPORTANT:
    We do NOT send the Whisper result through a second
    correction model.

    This prevents the correction model from returning
    an empty transcription.
    """

    print()
    print("=" * 60)
    print("SPEECH TO TEXT")
    print("=" * 60)

    try:

        # -------------------------------------------------
        # READ AUDIO
        # -------------------------------------------------

        # Make sure we start from the beginning
        try:
            audio_file.file.seek(0)
        except Exception:
            pass

        audio_bytes = audio_file.file.read()

        if not audio_bytes:

            raise ValueError(
                "Audio file is empty."
            )

        print(
            "Audio bytes:",
            len(audio_bytes)
        )

        print(
            "Filename:",
            getattr(
                audio_file,
                "filename",
                "unknown"
            )
        )

        # -------------------------------------------------
        # WHISPER TRANSCRIPTION
        # -------------------------------------------------

        print()
        print("Sending audio to Groq Whisper...")

        transcription = (
            client.audio.transcriptions.create(

                file=(
                    audio_file.filename
                    or "question.webm",
                    audio_bytes
                ),

                model=GROQ_STT_MODEL,

                response_format="json",

                temperature=0.0
            )
        )

        # -------------------------------------------------
        # GET TEXT
        # -------------------------------------------------

        raw_text = ""

        if transcription:

            raw_text = (
                getattr(
                    transcription,
                    "text",
                    ""
                )
                or ""
            )

        raw_text = raw_text.strip()

        # -------------------------------------------------
        # DEBUG
        # -------------------------------------------------

        print()
        print("-" * 60)
        print("RAW VOICE TRANSCRIPTION")
        print("-" * 60)

        print(raw_text)

        print("-" * 60)

        # -------------------------------------------------
        # EMPTY CHECK
        # -------------------------------------------------

        if not raw_text:

            raise ValueError(
                "Could not detect speech in the audio."
            )

        # -------------------------------------------------
        # RETURN WHISPER RESULT DIRECTLY
        # -------------------------------------------------

        print()
        print("Final transcription:")
        print(raw_text)

        print("=" * 60)

        return raw_text

    except Exception as error:

        print()
        print("=" * 60)
        print("SPEECH TO TEXT ERROR")
        print("=" * 60)

        print(
            type(error).__name__,
            ":",
            str(error)
        )

        print("=" * 60)

        raise


# =========================================================
# QUESTION UNDERSTANDING
# =========================================================

def understand_question(
    question,
    conversation=None
):

    if conversation is None:
        conversation = []

    # =====================================================
    # JSON SCHEMA
    # =====================================================

    schema = {

        "type": "object",

        "properties": {

            "intent": {

                "type": "string",

                "enum": [

                    "attendance_today",
                    "attendance_period",
                    "absent",
                    "leave",
                    "late",
                    "employee_summary",
                    "department_summary",
                    "attendance_percentage",
                    "unknown"
                ]
            },

            "period": {

                "type": "string",

                "enum": [

                    "today",
                    "yesterday",
                    "this_week",
                    "this_month",
                    "last_month",
                    "this_year",
                    "custom",
                    "all_time"
                ]
            },

            "employee_name": {

                "type": [
                    "string",
                    "null"
                ]
            },

            "department": {

                "type": [
                    "string",
                    "null"
                ]
            },

            "status": {

                "type": [
                    "string",
                    "null"
                ],

                "enum": [

                    "Present",
                    "Absent",
                    "Leave",
                    "Late",
                    None
                ]
            },

            "date_from": {

                "type": [
                    "string",
                    "null"
                ]
            },

            "date_to": {

                "type": [
                    "string",
                    "null"
                ]
            },

            "language": {

                "type": "string",

                "enum": [

                    "malayalam",
                    "english"
                ]
            }
        },

        "required": [

            "intent",
            "period",
            "employee_name",
            "department",
            "status",
            "date_from",
            "date_to",
            "language"
        ],

        "additionalProperties": False
    }

    # =====================================================
    # CONVERSATION CONTEXT
    # =====================================================

    context_text = ""

    if conversation:

        context_text = (
            "\nPrevious conversation:\n"
        )

        for message in conversation:

            role = message.get(
                "role",
                ""
            )

            content = message.get(
                "content",
                ""
            )

            context_text += (
                f"{role}: "
                f"{content}\n"
            )

    # =====================================================
    # GROQ REQUEST
    # =====================================================

    response = (
        client.chat.completions.create(

            model=GROQ_TEXT_MODEL,

            messages=[

                {
                    "role": "system",

                    "content":
                        QUERY_SYSTEM_PROMPT
                },

                {
                    "role": "user",

                    "content": (

                        context_text

                        +

                        "\nCurrent question:\n"

                        +

                        question
                    )
                }

            ],

            response_format={

                "type": "json_schema",

                "json_schema": {

                    "name":
                        "attendance_query",

                    "strict":
                        True,

                    "schema":
                        schema
                }
            },

            temperature=0
        )
    )

    # =====================================================
    # GET RESPONSE
    # =====================================================

    content = (
        response
        .choices[0]
        .message
        .content
    )

    # =====================================================
    # PARSE JSON
    # =====================================================

    query = json.loads(
        content
    )

    # =====================================================
    # DEBUG
    # =====================================================

    print()
    print("QUERY:")
    print(query)

    return query


# =========================================================
# FINAL ANSWER
# =========================================================

def generate_answer(
    question,
    query,
    result,
    conversation=None
):

    if conversation is None:
        conversation = []

    # =====================================================
    # PREPARE VERIFIED DATA
    # =====================================================

    data = {

        "question":
            question,

        "interpreted_query":
            query,

        "attendance_result":
            result
    }

    # =====================================================
    # CONVERSATION
    # =====================================================

    messages = [

        {
            "role":
                "system",

            "content":
                ANSWER_SYSTEM_PROMPT
        }
    ]

    # Only last 6 messages

    messages.extend(
        conversation[-6:]
    )

    messages.append({

        "role":
            "user",

        "content":
            json.dumps(
                data,
                ensure_ascii=False,
                default=str
            )
    })

    # =====================================================
    # GROQ ANSWER
    # =====================================================

    response = (
        client.chat.completions.create(

            model=GROQ_TEXT_MODEL,

            messages=messages,

            temperature=0.2,

            max_tokens=500
        )
    )

    answer = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    # =====================================================
    # DEBUG
    # =====================================================

    print()
    print("=" * 40)
    print("FINAL ANSWER")
    print("=" * 40)

    print(answer)

    print("=" * 40)

    return answer