from textual.widgets import Select, Button, Static
from textual.screen import ModalScreen
from textual.containers import Container

from pathlib import Path

from utils.resource_path import resource_path


class TemplateSelectModal(ModalScreen):
    def __init__(self):
        super().__init__()
        self.templates_dir = Path(resource_path("data/templates"))
        self.templates = self._load_template_names()

    def _load_template_names(self):
        """Load template names from the templates directory"""
        template_files = list(self.templates_dir.glob("*.md"))
        return [(f.stem.replace("-", " ").title(), f.name) for f in template_files]

    def compose(self):
        yield Container(
            Static("Select a template:"),
            Select(
                options=self.templates, value=self.templates[1][1], id="template_select"
            ),
            Button("Confirm", variant="primary", id="confirm"),
            Button("Cancel", variant="default", id="cancel"),
            classes="template-modal",
        )

    def _on_mount(self, event):
        self.focus_next("#confirm")
        return super()._on_mount(event)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            selected = self.query_one("#template_select").value
            if selected:
                template_path = self.templates_dir / selected
                with open(template_path, "r") as f:
                    template_content = f.read()
                self.dismiss((True, template_content))
            else:
                self.dismiss((False, None))
        else:
            self.dismiss((False, None))

    def _on_key(self, event):
        if event.key == "escape":
            self.dismiss((False, None))
            # stop the bubbling of the event
            event.stop()
            return
        return super()._on_key(event)
