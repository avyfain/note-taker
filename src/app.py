import datetime
from typing import Optional

from rich.panel import Panel
from rich import box

from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Static, ListView, ListItem
from textual.containers import Grid
from textual.widgets import Header, Static, Footer, TextArea, Button, Label
from textual.screen import Screen, ModalScreen
from textual.binding import Binding

from llm.model import LanguageModel
from notes.manager import NoteManager
from audio.textual_transcription_textarea import TranscriptionTextArea


class NotePanel(Static):
    def __init__(self, title: str, content: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.content = content

    def render(self):
        return Panel(
            self.content,
            title=self.title,
            border_style="cyan",
            box=box.ROUNDED,
            expand=True,
        )


class NoteListView(ListView):
    def __init__(self, node_select_callback: callable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.note_manager = NoteManager()
        self.node_select_callback = node_select_callback

    def on_list_view_selected(self, selected: ListView.Selected):
        self.note_manager.select_note_by_index(selected.list_view.index)
        self.node_select_callback()

    def compose(self):
        notes = self.note_manager.list_notes()
        for note in notes:
            content = self.note_manager.read_note(note["uuid"])
            yield ListItem(
                NotePanel(
                    note["title"],
                    (content[:50] + "..." if len(content) > 50 else content),
                )
            )


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


class DeleteScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Delete Note?", id="question"),
            Button("Delete", variant="error", id="delete"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete":
            self.dismiss(True)
        else:
            self.dismiss(False)


class RichNoteTakingScreen(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
        ("n", "new_note", "New"),
        ("l", "live_note", "New Live"),
        ("d", "delete_note", "Delete"),
    ]
    CSS_PATH = "main.tcss"

    current_selected_index: Optional[int] = None

    def __init__(self):
        super().__init__()
        self.note_manager = NoteManager()

    def compose(self):
        yield Header()
        yield NoteListView(self.action_edit_note, id="note_list")
        yield Footer()

    def action_new_note(self):
        self.note_manager.selected_note = None
        self.action_edit_note()

    @work
    async def action_edit_note(self):
        await self.app.push_screen_wait(NoteEditScreen())
        self.app.pop_screen()
        self.app.push_screen(RichNoteTakingScreen())

    @work
    async def action_live_note(self):
        await self.app.push_screen_wait(LiveNoteEditScreen())
        self.app.pop_screen()
        self.app.push_screen(RichNoteTakingScreen())

    def action_quit(self):
        self.app.exit()

    def action_delete_note(self):
        def check_delete(delete: bool | None) -> None:
            """Called when the delete screen is dismissed"""
            if delete:
                highlighted_note_index = self.query_one("#note_list").index
                self.note_manager.delete_note_by_index(highlighted_note_index)
                self.app.pop_screen()
                self.app.push_screen(RichNoteTakingScreen())

        self.app.push_screen(DeleteScreen(), check_delete)


class RichNoteTakingApp(App):
    def on_mount(self):
        self.push_screen(RichNoteTakingScreen())
