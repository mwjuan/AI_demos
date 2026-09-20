from pathlib import Path

from dotenv import load_dotenv


LESSON_DIRECTORY = Path(__file__).resolve().parents[2]


def load_lesson_environment() -> None:
    load_dotenv(LESSON_DIRECTORY / ".env")

