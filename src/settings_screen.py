from textual.containers import Grid, Vertical
from textual.widgets import Select, TextArea, Button, Label
from textual.screen import ModalScreen
from textual.message import Message

class SettingsScreen(ModalScreen):
    """A modal screen for managing LLM settings."""

    class SettingsChanged(Message):
        """Settings changed message."""
        def __init__(self, prompt: str, model: str) -> None:
            self.prompt = prompt
            self.model = model
            super().__init__()

    def __init__(self, current_prompt: str = "", current_model: str = "gpt-3.5-turbo"):
        super().__init__()
        self.current_prompt = current_prompt
        self.current_model = current_model

    BINDINGS = [("escape", "cancel", "Cancel")]

    def compose(self):
        yield Grid(
            Vertical(
                Label("LLM Settings", id="settings-title", classes="settings-header"),
                Label("System Prompt:"),
                TextArea(
                    id="prompt-input",
                    language="markdown",
                    value=self.current_prompt,
                    classes="settings-prompt"
                ),
                Label("Model:"),
                Select(
                    [(model, model) for model in [
                        "gpt-3.5-turbo",
                        "gpt-4",
                        "claude-3-opus",
                        "claude-3-sonnet",
                        "claude-3-haiku"
                    ]],
                    id="model-select",
                    value=self.current_model,
                    classes="settings-select"
                ),
                Grid(
                    Button("Save", variant="primary", id="save"),
                    Button("Cancel", variant="default", id="cancel"),
                    id="button-container",
                    classes="settings-buttons"
                ),
                id="settings-container"
            ),
            id="settings-dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            prompt = self.query_one("#prompt-input").text
            model = self.query_one("#model-select").value
            self.post_message(self.SettingsChanged(prompt, model))
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_cancel(self):
        self.dismiss(False)
