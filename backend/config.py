import os

from dotenv import load_dotenv


# =========================================================
# LOAD .ENV
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ENV_FILE = os.path.join(
    BASE_DIR,
    ".env"
)

# override=True is IMPORTANT
# It makes the .env value override an old
# environment variable already stored in Windows.
load_dotenv(
    ENV_FILE,
    override=True
)


# =========================================================
# GROQ
# =========================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
).strip()

GROQ_TEXT_MODEL = os.getenv(
    "GROQ_TEXT_MODEL",
    "openai/gpt-oss-20b"
).strip()

GROQ_STT_MODEL = os.getenv(
    "GROQ_STT_MODEL",
    "whisper-large-v3-turbo"
).strip()


# =========================================================
# GOOGLE APPS SCRIPT
# =========================================================

APPS_SCRIPT_URL = os.getenv(
    "APPS_SCRIPT_URL",
    ""
).strip()

APPS_SCRIPT_SECRET = os.getenv(
    "APPS_SCRIPT_SECRET",
    ""
).strip()


# =========================================================
# TIMEZONE
# =========================================================

TIMEZONE = os.getenv(
    "TIMEZONE",
    "Asia/Kolkata"
).strip()


# =========================================================
# VALIDATION
# =========================================================

def validate_config():

    errors = []


    # -----------------------------------------------------
    # GROQ API KEY
    # -----------------------------------------------------

    if not GROQ_API_KEY:

        errors.append(
            "GROQ_API_KEY is missing."
        )

    elif not GROQ_API_KEY.startswith("gsk_"):

        errors.append(
            "GROQ_API_KEY does not start with gsk_."
        )


    # -----------------------------------------------------
    # GROQ MODEL
    # -----------------------------------------------------

    if not GROQ_TEXT_MODEL:

        errors.append(
            "GROQ_TEXT_MODEL is missing."
        )


    if not GROQ_STT_MODEL:

        errors.append(
            "GROQ_STT_MODEL is missing."
        )


    # -----------------------------------------------------
    # APPS SCRIPT
    # -----------------------------------------------------

    if not APPS_SCRIPT_URL:

        errors.append(
            "APPS_SCRIPT_URL is missing."
        )


    if not APPS_SCRIPT_SECRET:

        errors.append(
            "APPS_SCRIPT_SECRET is missing."
        )


    # -----------------------------------------------------
    # ERROR
    # -----------------------------------------------------

    if errors:

        raise RuntimeError(
            "\n".join(errors)
        )


    # -----------------------------------------------------
    # SAFE DEBUG INFORMATION
    # -----------------------------------------------------

    print(
        "Groq configuration:",
        GROQ_API_KEY[:4],
        "length=",
        len(GROQ_API_KEY),
        "model=",
        GROQ_TEXT_MODEL
    )

    print(
        "Apps Script configuration: OK"
    )

    print(
        "Timezone:",
        TIMEZONE
    )


# =========================================================
# STARTUP VALIDATION
# =========================================================

if __name__ == "__main__":

    validate_config()