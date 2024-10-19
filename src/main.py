import multiprocessing
from dotenv import load_dotenv
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

    app = RichNoteTakingApp()
    app.run()
