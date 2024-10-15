import wave
import time
from queue import Queue
from typing import List, Callable

import numpy as np
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console
from rich.text import Text

from audio.AudioCapture import AudioCapture
from audio.whisper_transcribe import ContinuousTranscriberProcess


class TranscriptionManager:
    def __init__(self, console: Console):
        self.console = console
        self.transcriptions: List[str] = []
        self.partial_transcription = ""
        self.update_queue = Queue()
        self.user_input = ""
        self.is_transcribing = False
        self.wav_file = None
        self.transcriber = None
        self.audio_capture = None

    def generate_transcription_content(self, panel_height: int):
        # Calculate the number of visible lines based on panel height
        # Subtract 2 for the panel border and 1 for the partial transcription
        max_visible_lines = 15

        # Combine full transcriptions and partial transcription
        all_content = self.transcriptions + [f"{panel_height} Partial: {self.partial_transcription}"]

        # Get the last `max_visible_lines` of content
        visible_content = all_content[-max_visible_lines:]

        # Join the visible content into a single string
        content = "\n".join(visible_content)

        # Create a Text object for rich formatting
        text = Text(content)

        # Highlight the partial transcription
        if self.partial_transcription:
            text.highlight_words(["Partial:"], style="bold yellow")

        return Panel(text, title="Transcriptions", border_style="green", expand=True)

    def generate_user_input_content(self):
        return Panel(
            self.user_input, title="Your Input", border_style="blue", expand=True
        )

    def create_layout(self) -> Layout:
        layout = Layout(name="root")
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3),
        )
        layout["root"]["main"].split(
            Layout(name="transcriptions"), Layout(name="user_input", size=3)
        )
        return layout

    def update_layout(self, layout: Layout, full_update: bool = False):
        if full_update:
            layout["header"].update(
                Panel("Rich Note Taking App - Transcribing...", style="bold magenta")
            )

        # Calculate the height of the transcriptions panel
        _, height = self.console.measure(layout["main"])
        transcriptions_height = height

        # Update the transcriptions panel with the calculated height
        layout["transcriptions"].update(
            self.generate_transcription_content(transcriptions_height)
        )

        layout["user_input"].update(self.generate_user_input_content())

        if full_update:
            layout["footer"].update(
                Panel(
                    "Press 'Esc' to stop transcribing | 'Enter' to submit your input",
                    style="italic",
                )
            )

    def process_transcription(self, transcription: str, is_partial: bool):
        if not transcription or len(transcription.strip()) == 0:
            return
        if is_partial:
            self.partial_transcription = transcription
        else:
            self.transcriptions.append(transcription)
            self.partial_transcription = ""
        self.update_queue.put(True)  # Signal that an update is available

    def update_transcriptions(self):
        updated = False
        while not self.update_queue.empty():
            self.update_queue.get()
            updated = True
        return updated

    def send_audio_to_transcriber(self, audio_data: np.ndarray):
        self.transcriber.process(audio_data)
        if self.wav_file is not None:
            audio_data_int = (audio_data * 32767).astype(np.int16)
            self.wav_file.writeframes(audio_data_int.tobytes())

    def handle_user_input(self, key):
        if key == "\x1b":  # Escape key
            return False
        elif key == "\r":  # Enter key
            self.transcriptions.append(f"Typed: {self.user_input}")
            self.user_input = ""
        elif key == "\x7f":  # Backspace key
            self.user_input = self.user_input[:-1]
        else:
            self.user_input += key
        return True

    def start_transcription(self, on_update: Callable[[Layout], None]):
        self.console.print("[bold]Starting transcription. Press 'Esc' to stop.[/bold]")

        self.wav_file = wave.open("streaming_recording.wav", "wb")
        self.wav_file.setnchannels(1)
        self.wav_file.setsampwidth(2)
        self.wav_file.setframerate(16000)

        self.transcriber = ContinuousTranscriberProcess(self.process_transcription)
        self.audio_capture = AudioCapture(self.send_audio_to_transcriber)

        self.transcriber.start()
        self.audio_capture.start_recording()
        self.is_transcribing = True

        while self.is_transcribing:
            if self.update_transcriptions():
                on_update()
            yield

        self.stop_transcription()

    def stop_transcription(self):
        self.is_transcribing = False
        if self.transcriber:
            self.transcriber.stop()
        if self.audio_capture:
            self.audio_capture.stop_recording()
        if self.wav_file:
            self.wav_file.close()
        self.console.print("[bold green]Transcription completed.[/bold green]")

    def get_transcriptions(self):
        return self.transcriptions

    def reset(self):
        self.transcriptions = []
        self.user_input = ""
        self.partial_transcription = ""
