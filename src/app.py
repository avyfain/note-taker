import os
import platform
import subprocess
from typing import Optional

from rich.panel import Panel
from rich import box

from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Static, ListView, ListItem
from textual.containers import Grid
from textual.widgets import Header, Static, Footer, Button, Label
from textual.screen import Screen, ModalScreen
from textual.binding import Binding

from notes.manager import NoteManager
from notes_editor_components import NoteEditScreen, LiveNoteEditScreen
from settings_screen import SettingsScreen
from utils.helpers import open_folder_with_finder


class NotePanel(Static):
    def __init__(self, title: str, content: str, note_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.content = content
        self.note_id = note_id

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
        self.note_manager.select_note_by_uuid(selected.item.children[0].note_id)
        self.node_select_callback()

    def compose(self):
        notes = self.note_manager.list_notes(True)
        for note in notes:
            content = self.note_manager.read_note(note["uuid"])
            yield ListItem(
                NotePanel(
                    note["title"],
                    (content[:50] + "..." if len(content) > 50 else content),
                    note["uuid"],
                )
            )


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
        ("s", "settings", "Settings"),
        Binding("ctrl+g", "github", "GitHub", show=True, priority=True),
        Binding("ctrl+f", "folder", "Notes Folder", show=True, priority=True),
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

    @work
    async def action_settings(self):
        await self.app.push_screen_wait(SettingsScreen())
        self.app.pop_screen()
        self.app.push_screen(RichNoteTakingScreen())

    def action_github(self):
        # use the system open command to open the browser
        url = "https://github.com/locaal-ai/note-taker?tab=readme-ov-file#local-ai-note-taking-app"
        import webbrowser

        webbrowser.open(url)

    def action_folder(self):
        path = self.note_manager.get_notes_directory()
        open_folder_with_finder(path)

    def action_quit(self):
        self.app.exit()

    def action_delete_note(self):
        def check_delete(delete: bool | None) -> None:
            """Called when the delete screen is dismissed"""
            if delete:
                highlighted_item = self.query_one("#note_list").highlighted_child
                note_id = highlighted_item.children[0].note_id
                self.note_manager.delete_note(note_id)
                self.app.pop_screen()
                self.app.push_screen(RichNoteTakingScreen())

        self.app.push_screen(DeleteScreen(), check_delete)


class RichNoteTakingApp(App):
    def on_mount(self):
        self.push_screen(RichNoteTakingScreen())
