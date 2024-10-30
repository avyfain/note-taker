import os
from dotenv import load_dotenv
from audio.Transcriber import Transcriber
from app import RichNoteTakingApp
from llm.model import LanguageModel
from utils import resource_path


if __name__ == "__main__":
    print("Starting Note Taker")

    load_dotenv(resource_path.resource_path(".env"))

    Transcriber()  # Warm up the Transcriber
    LanguageModel()  # Warm up the LLM

    app = RichNoteTakingApp()
    app.title = "Locaal AI Note Taker"
    # get the version from the .env file
    version = os.getenv("LOCAL_RELEASE_TAG")
    app.sub_title = f"Version: {version}"
    app.run()
