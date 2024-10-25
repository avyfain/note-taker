from dotenv import load_dotenv
from app import RichNoteTakingApp
from audio.Transcriber import Transcriber
from llm.model import LanguageModel
from utils import resource_path


if __name__ == "__main__":
    print("Starting Note Taker")

    load_dotenv(resource_path.resource_path(".env"))

    Transcriber()  # Warm up the Transcriber
    LanguageModel()  # Warm up the LLM

    app = RichNoteTakingApp()
    app.run()
