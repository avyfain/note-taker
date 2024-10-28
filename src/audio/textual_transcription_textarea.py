from os import path
from queue import Queue
import time
from typing import List
import numpy as np
from textual.widgets import TextArea
from textual import on, work
from textual.message import Message
from textual.worker import get_current_worker
import wave

from audio.Transcriber import Transcriber
from audio.AudioCapture import AudioCapture
from notes.manager import NoteManager


class TranscriptionTextArea(TextArea):
    def __init__(self, uuid: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transcriptions: List[str] = []
        self.partial_transcription = ""
        self.update_queue = Queue()
        self.is_transcribing = False
        self.wav_file = None
        self.uuid = uuid
        self.transcriber = Transcriber()
        self.audio_capture = None
        self.read_only = True
        self.text = "Transcription will appear here."
        self.note_manager = NoteManager()
        self.start_transcription()

    def on_unmount(self):
        self.stop_transcription()

    def generate_transcription_content(self):
        # Combine full transcriptions and partial transcription
        all_content = self.transcriptions + [f"\n\n(p) {self.partial_transcription}\n"]

        # Join the visible content into a single string
        content = "\n".join(all_content)

        return content

    def process_transcription(
        self, chunk_id: int, transcription: str, is_partial: bool
    ):
        if not transcription or len(transcription) == 0:
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
        self.transcriber.queue_audio(audio_data)
        if self.wav_file is not None:
            audio_data_int = (audio_data * 32767).astype(np.int16)
            self.wav_file.writeframes(audio_data_int.tobytes())

    class Update(Message):
        def __init__(self, transcription: str):
            self.transcription = transcription
            super().__init__()

    @on(Update)
    def update_ui(self, update: Update):
        self.text = update.transcription
        # write the transcription to the note
        self.note_manager.update_note_transcription(self.uuid, self.text)
        # set the cursor to the last line
        self.cursor_location = (len(self.text.split("\n")) + 1, 0)

    @work(thread=True)
    def start_transcription(self):
        self.app.notify("Starting transcription.")
        self.wav_file = wave.open(
            path.join(
                self.note_manager.get_notes_directory(), "streaming_recording.wav"
            ),
            "wb",
        )
        self.wav_file.setnchannels(1)
        self.wav_file.setsampwidth(2)
        self.wav_file.setframerate(16000)

        self.audio_capture = AudioCapture(self.send_audio_to_transcriber)

        self.transcriber.start(self.process_transcription)
        self.audio_capture.start_recording()
        self.is_transcribing = True

        worker = get_current_worker()

        while self.is_transcribing and not worker.is_cancelled:
            if self.update_transcriptions():
                self.post_message(self.Update(self.generate_transcription_content()))
            # sleep for a short time to avoid busy loop
            time.sleep(0.1)

        self.log.info("Transcription thread end.")
        self.app.notify("Transcription thread end.")

    def stop_transcription(self):
        self.app.notify("Stopping transcription.")
        self.is_transcribing = False
        if self.transcriber:
            self.transcriber.stop()
            self.transcriber = None
        if self.audio_capture:
            self.audio_capture.stop_recording()
            self.audio_capture = None
        if self.wav_file:
            self.wav_file.close()
            self.wav_file = None
        self.app.notify("Transcription stopped.")
        self.app.workers.cancel_all()
