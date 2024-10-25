import datetime

from textual.widgets import Static
from textual.widgets import Static, Footer, TextArea
from textual.screen import Screen
from textual.binding import Binding
from textual import work

from llm.model import LanguageModel
from notes.manager import NoteManager

from audio.textual_transcription_textarea import TranscriptionTextArea


class NoteTextArea(TextArea):
    BINDINGS = []

    def __init__(self, uuid: str, content: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = "markdown"
        self.note_manager = NoteManager()
        self.content = content
        self.uuid = uuid
        self.text = self.content

    def on_mount(self):
        if self.text and len(self.text) > 0:
            lines = self.text.split("\n")
            self.cursor_location = (len(lines) - 1, len(lines[-1]))

    def on_text_area_changed(self, changed: TextArea.Changed):
        self.note_manager.update_note_content(self.uuid, changed.text_area.text)


class NoteEditScreen(Screen):
    BINDINGS = [
        ("escape", "quit", "Quit"),
        Binding("ctrl+l", "run_llm", "Run LLM", show=True, priority=True),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.note_manager = NoteManager()
        if self.note_manager.selected_note is None:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            self.title = today
            # add todays date to the title
            self.content = f"# Notes {today}\n\n"
            self.uuid = self.note_manager.create_note(self.title, self.content)
        else:
            note = self.note_manager.selected_note
            self.title = note["title"]
            self.content = self.note_manager.read_note(note["uuid"])
            self.uuid = note["uuid"]

    def compose(self):
        yield Static(f"Title: {self.title}")
        yield NoteTextArea(self.uuid, self.content, id="note_text")
        yield Footer()

    def action_quit(self):
        self.app.notify("Note Saved", timeout=1)
        new_content = self.query_one("#note_text").text
        self.note_manager.update_note_content(self.uuid, new_content)
        self.dismiss()

    @work
    async def action_run_llm(self):
        self.app.notify("Running LLM")
        textArea = self.query_one("#note_text")
        note_content = textArea.text
        textArea.text += f"\n\n# Response\n\n"
        for response in LanguageModel().generate_response(note_content):
            self.log.info(response)
            textArea.text += response


class LiveNoteEditScreen(Screen):
    BINDINGS = [
        ("escape", "quit", "Quit"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.note_manager = NoteManager()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.title = today
        # add todays date to the title
        self.content = f"# Notes {today}\n\n"
        self.uuid = self.note_manager.create_note(self.title, self.content)

    def compose(self):
        yield Static(f"Title: {self.title}")
        yield TranscriptionTextArea(id="Transcription")
        text_area = NoteTextArea(self.uuid, self.content, id="note_text")
        text_area.focus()
        yield text_area

    def action_quit(self):
        self.app.notify("Note Saved")
        note_content = self.query_one("#note_text").text
        transcription = self.query_one("#Transcription").text
        combined = f"{note_content}\n\n# Transcription\n\n{transcription}"
        self.note_manager.update_note_content(self.uuid, combined)
        self.dismiss()
