import multiprocessing
from dotenv import load_dotenv
import faster_whisper
from app import RichNoteTakingApp
from llm.model import LanguageModel
from utils import resource_path
import os


if __name__ == "__main__":
    # On Windows calling this function is necessary.
    multiprocessing.freeze_support()

    print("Starting Note Taker")
    
    load_dotenv(resource_path.resource_path(".env"))

    LanguageModel()  # Warm up the LLM
    faster_whisper.WhisperModel(
        "small.en",
        device=os.environ["WHISPER_EXEC_BACKEND"],
        compute_type=os.environ["WHISPER_COMPUTE_TYPE"],
    )

    app = RichNoteTakingApp()
    app.run()
