from dotenv import load_dotenv
import faster_whisper
from app import RichNoteTakingApp
from llm.model import LanguageModel
from utils import resource_path
import os

load_dotenv(resource_path.resource_path(".env"))

if __name__ == "__main__":
    print("Starting Note Taker")

    LanguageModel()  # Warm up the LLM
    faster_whisper.WhisperModel(
        "small.en",
        device=os.environ["WHISPER_EXEC_BACKEND"],
        compute_type=os.environ["WHISPER_COMPUTE_TYPE"],
    )

    app = RichNoteTakingApp()
    app.run()
