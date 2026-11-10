from pathlib import Path

from backend.voice_service import (
    process_voice_question
)


class AudioFile:

    def __init__(
        self,
        path
    ):

        self.filename = Path(
            path
        ).name

        self.file = open(
            path,
            "rb"
        )

    def close(self):

        self.file.close()


print()
print("=" * 70)
print("HR SAARATHI - VOICE TEST")
print("=" * 70)


AUDIO_FILE = "malayalam_question.wav"


if not Path(AUDIO_FILE).exists():

    print()
    print("❌ AUDIO FILE NOT FOUND")

    print()
    print(
        "Place this file in:"
    )

    print(
        Path(AUDIO_FILE).absolute()
    )

    raise SystemExit


audio = AudioFile(
    AUDIO_FILE
)


try:

    result = process_voice_question(
        audio
    )


    print()
    print("=" * 70)
    print("VOICE RESULT")
    print("=" * 70)


    print()
    print("🎤 TRANSCRIPTION:")

    print(
        result["question"]
    )


    print()
    print("🧠 INTERPRETED QUERY:")

    print(
        result["query"]
    )


    print()
    print("📊 ATTENDANCE RESULT:")

    print(
        result["result"]
    )


    print()
    print("🤖 HR SAARATHI ANSWER:")

    print(
        result["answer"]
    )


    print()
    print("=" * 70)
    print("VOICE TEST SUCCESSFUL ✅")
    print("=" * 70)


except Exception as e:

    print()
    print("=" * 70)
    print("❌ VOICE TEST FAILED")
    print("=" * 70)

    print()
    print(
        type(e).__name__
        + ": "
        + str(e)
    )


finally:

    audio.close()