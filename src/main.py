import cmd
import os
import sys
import time
import select
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live

from notes.manager import NoteManager
from llm.processor import process_with_llm
from audio.rich_transcription_manager import TranscriptionManager

# Import platform-specific modules
if os.name == "nt":  # For Windows
    import msvcrt
else:  # For Unix-like systems
    import termios
    import tty
    import select


class NoteTakingApp(cmd.Cmd):
    intro = "Welcome to the Rich Note Taking App. Type 'help' for a list of commands."
    prompt = "(notes) "

    def __init__(self):
        super().__init__()
        self.note_manager = NoteManager()
        self.console = Console()
        self.transcription_manager = TranscriptionManager(self.console)

    def do_add(self, arg):
        """Add a new note: add <title>"""
        title = arg.strip()
        if not title:
            self.console.print(
                "[bold red]Please provide a title for the note.[/bold red]"
            )
            return
        content = self.console.input("[cyan]Enter note content: [/cyan]")
        self.note_manager.create_note(title, content)
        self.console.print(
            f"[bold green]Note '{title}' added successfully.[/bold green]"
        )

    def do_list(self, arg):
        """List all notes"""
        notes = self.note_manager.list_notes()
        for note in notes:
            panel = Panel(
                f"{note['content'][:50]}...",
                title=note["title"],
                expand=False,
                border_style="cyan",
            )
            self.console.print(panel)

    def non_blocking_input(self):
        if os.name == "nt":  # For Windows
            if msvcrt.kbhit():
                return msvcrt.getch().decode("utf-8")
        else:  # For Unix-like systems
            old_settings = termios.tcgetattr(sys.stdin)
            try:
                tty.setcbreak(sys.stdin.fileno())
                if select.select([sys.stdin], [], [], 0)[0]:
                    return sys.stdin.read(1)
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        return None

    def do_transcribe(self, arg):
        """Capture audio and transcribe it into a note"""
        layout = self.transcription_manager.create_layout()
        self.transcription_manager.update_layout(layout, full_update=True)

        def on_update():
            self.transcription_manager.update_layout(layout)
            live.update(layout)

        with Live(layout, refresh_per_second=10, screen=True) as live:
            for _ in self.transcription_manager.start_transcription(on_update):
                key = self.non_blocking_input()
                if key:
                    if key == "\x1b":  # Escape key
                        self.transcription_manager.stop_transcription()
                        break
                    if not self.transcription_manager.handle_user_input(key):
                        break
                time.sleep(0.1)

        # create a note with the transcriptions, the title can just be the date and time
        title = time.strftime("%Y-%m-%d %H:%M:%S")
        content = "\n".join(self.transcription_manager.get_transcriptions())
        self.note_manager.create_note(title, content)

        self.transcription_manager.reset()

        # show the new note
        self.do_list("")

    def do_ask(self, arg):
        """Ask a question to the LLM based on your notes"""
        if not arg:
            self.console.print(
                "[bold red]Please provide a query for the LLM.[/bold red]"
            )
            return
        notes = self.note_manager.get_all_notes()
        context = "\n".join([f"{note['title']}: {note['content']}" for note in notes])

        with self.console.status(
            "[bold green]Processing query with LLM...[/bold green]"
        ):
            response = process_with_llm(arg, context)

        self.console.print(
            Panel(response, title="LLM Response", border_style="blue", expand=False)
        )

    def do_exit(self, arg):
        """Exit the application"""
        self.console.print(
            "[bold]Thank you for using the Rich Note Taking App. Goodbye![/bold]"
        )
        return True

    def default(self, line):
        self.console.print(f"[bold red]Unknown command: {line}[/bold red]")
        self.console.print("Type 'help' for a list of available commands.")


if __name__ == "__main__":
    NoteTakingApp().cmdloop()
