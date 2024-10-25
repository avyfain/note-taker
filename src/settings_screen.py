from textual.containers import Grid, Vertical
from textual.widgets import Select, TextArea, Button, Label, Header, Footer
from textual.screen import ModalScreen
from textual.message import Message
from utils.storage import store_data, fetch_data
from utils.defaults import default_prompt, default_model
from huggingface_hub import list_repo_files
import re


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

    BINDINGS = [("escape", "exit", "Exit")]

    def __init__(self):
        super().__init__()
        self.current_prompt = fetch_data("settings.json", "prompt", default_prompt)
        self.current_model = fetch_data("settings.json", "model", default_model)

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
                Label("Model:"),
                Select(
                    [
                        (model, model)
                        for model in [
                            "bartowski/Llama-3.2-1B-Instruct-GGUF",
                            "MaziyarPanahi/Llama-3.2-1B-Instruct-GGUF",
                            "unsloth/Llama-3.2-1B-Instruct-GGUF",
                            "lmstudio-community/Llama-3.2-1B-Instruct-GGUF",
                            "MaziyarPanahi/SmolLM-1.7B-Instruct-v0.2-GGUF",
                            "bartowski/Phi-3.5-mini-instruct_Uncensored-GGUF",
                        ]
                    ],
                    id="model-select",
                    value=self.current_model,
                    classes="settings-select",
                ),
                id="settings-container",
            ),
            id="settings-dialog",
        )
        yield Footer()

    def on_select_changed(self, changed: Select.Changed):
        if changed.select.id == "model-select":
            self.current_model = changed.select.value
            store_data("settings.json", "model", self.current_model)
            model_file = find_q4_model_file(self.current_model)
            store_data("settings.json", "model_file", model_file)
            self.notify("Model updated.")

    def on_text_area_changed(self, changed: TextArea.Changed):
        if changed.text_area.id == "prompt-input":
            self.current_prompt = changed.text_area.text
            store_data("settings.json", "prompt", self.current_prompt)

    def action_exit(self):
        self.notify("Settings updated.")
        self.dismiss(False)
