import json
from textual.containers import Grid, Vertical
from textual.widgets import Select, TextArea, Button, Label, Header, Footer, Input
from textual.screen import ModalScreen
from textual.message import Message
from textual.binding import Binding
from notes.manager import default_storage_folder
from utils.helpers import open_folder_with_finder
from utils.storage import get_data_dir, store_data, fetch_data
from utils.defaults import default_system_prompt, default_model, default_query_template
from utils.resource_path import resource_path
from huggingface_hub import list_repo_files
import re


# Load models from the JSON file
def load_transcription_models():
    with open(resource_path("data/models_directory.json"), "r") as file:
        models = json.load(file)["models"]
    # keep models which don't have a "extra" field
    models = [model for model in models if "extra" not in model]
    # keep models that are transcription type
    models = [model for model in models if model["type"] == "MODEL_TYPE_TRANSCRIPTION"]
    # sort models by friendly name
    models = sorted(models, key=lambda x: x["friendly_name"])
    # turn into Select options format (tuple of model name)
    models = [(model["friendly_name"], model["local_folder_name"]) for model in models]
    return models


def find_q4_model_file(repo_id):
    """
    Find a Q4 quantized model file in a Hugging Face repository.

    Args:
        repo_id (str): Repository ID in format "username/repository"

    Returns:
        str: Filename of the Q4 model if found, None otherwise
    """
    try:
        # List all files in the repository
        files = list_repo_files(repo_id)

        # Look for files containing 'q4' in their name (case insensitive)
        q4_files = [f for f in files if re.search(r"q4", f, re.IGNORECASE)]

        # Filter for common model extensions
        model_extensions = (".bin", ".gguf")
        q4_model_files = [f for f in q4_files if f.lower().endswith(model_extensions)]

        if q4_model_files:
            return q4_model_files[0]  # Return the first matching file

        return None

    except Exception as e:
        print(f"Error accessing repository: {e}")
        return None


class SettingsScreen(ModalScreen):
    """A modal screen for managing the settings."""

    BINDINGS = [
        ("escape", "exit", "Exit"),
        Binding("ctrl+f", "folder", "Open Settings Folder", show=True, priority=True),
    ]

    def __init__(self):
        super().__init__()
        self.current_prompt = fetch_data(
            "settings.json", "prompt", default_system_prompt
        )
        self.current_model = fetch_data("settings.json", "model", default_model)
        self.current_whisper_model = fetch_data(
            "settings.json", "whisper_model", "ggml-model-whisper-small-en-q5_1"
        )
        self.storage_folder = fetch_data(
            "settings.json", "storage_folder", default_storage_folder
        )
        self.current_query = fetch_data(
            "settings.json", "query", default_query_template
        )

    def compose(self):
        yield Header("Settings")
        yield Grid(
            Vertical(
                Label("LLM Settings", id="settings-title", classes="settings-header"),
                Label("System Prompt:"),
                TextArea(
                    id="prompt-input",
                    text=self.current_prompt,
                    classes="settings-prompt",
                ),
                Label("Query format:"),
                TextArea(
                    id="query-input",
                    text=self.current_query,
                    classes="settings-query",
                ),
                Label("LLM Model:"),
                Select(
                    [
                        (model, model)
                        for model in [
                            "bartowski/Llama-3.2-1B-Instruct-GGUF",
                            "bartowski/SmolLM2-1.7B-Instruct-GGUF",
                            "bartowski/Phi-3.5-mini-instruct-GGUF",
                            "MaziyarPanahi/Llama-3.2-1B-Instruct-GGUF",
                            "MaziyarPanahi/Qwen2-1.5B-Instruct-GGUF",
                            "unsloth/Llama-3.2-1B-Instruct-GGUF",
                            "lmstudio-community/Llama-3.2-1B-Instruct-GGUF",
                            "lmstudio-community/Qwen2.5-1.5B-Instruct-GGUF",
                            "lmstudio-community/SmolLM2-360M-Instruct-GGUF",
                            "HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF",
                        ]
                    ],
                    id="model-select",
                    value=self.current_model,
                    classes="settings-select",
                ),
                Label("Transcription Model:"),
                Select(
                    load_transcription_models(),
                    id="whisper-model-select",
                    value=self.current_whisper_model,
                    classes="settings-select",
                    name="whisper-model",
                ),
                Label(
                    "Storage Folder:",
                    classes="settings-storage-folder",
                ),
                Input(self.storage_folder, id="storage-folder-input"),
                id="settings-container",
            ),
            id="settings-dialog",
        )
        yield Footer()

    def on_select_changed(self, changed: Select.Changed):
        if changed.select.id == "model-select":
            self.current_model = changed.select.value
            model_file = find_q4_model_file(self.current_model)
            if model_file is None:
                self.notify("Q4 model file not found.")
                return
            store_data("settings.json", "model_file", model_file)
            store_data("settings.json", "model", self.current_model)
            self.notify("Model updated.")
        elif changed.select.id == "whisper-model-select":
            self.current_whisper_model = changed.select.value
            store_data("settings.json", "whisper_model", self.current_whisper_model)
            self.notify("Whisper model updated.")

    def on_text_area_changed(self, changed: TextArea.Changed):
        if changed.text_area.id == "prompt-input":
            self.current_prompt = changed.text_area.text
            store_data("settings.json", "prompt", self.current_prompt)
        elif changed.text_area.id == "query-input":
            self.current_query = changed.text_area.text
            store_data("settings.json", "query", self.current_query)

    def on_input_changed(self, changed: Input.Changed):
        if changed.input.id == "storage-folder-input":
            self.storage_folder = changed.value
            store_data("settings.json", "storage_folder", self.storage_folder)

    def action_exit(self):
        self.notify("Settings updated.")
        self.dismiss(False)

    def action_folder(self):
        path = get_data_dir()
        open_folder_with_finder(path)
