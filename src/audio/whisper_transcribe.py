import time
import numpy as np
import faster_whisper
import threading
import multiprocessing as mp
from textual import log
from dotenv import load_dotenv
import os
from utils import resource_path

load_dotenv(resource_path.resource_path(".env"))


class ContinuousTranscriberProcess:
    def __init__(
        self,
        callback,
    ):
        self.callback = callback
        self.buffer_duration = 10
        self.sample_rate = 16000
        self.buffer_size = self.buffer_duration * self.sample_rate
        self.input_queue = mp.Queue()
        self.result_queue = mp.Queue()
        self.stop_event = mp.Event()
        self.transcription_process = None
        self.result_thread = threading.Thread(target=self._result_loop)

    def process(self, audio_data: np.ndarray):
        # check if the process is running
        if not self.is_running():
            return

        # check if the audio data is float32
        if audio_data.dtype != np.float32:
            raise ValueError("Audio data must be float32")

        # put the audio data into the queue
        self.input_queue.put(audio_data)

    def start(self):
        if (
            self.transcription_process is None
            or not self.transcription_process.is_alive()
        ):
            self.transcription_process = mp.Process(
                target=ContinuousTranscriberProcess._transcribe_loop,
                args=(
                    self.input_queue,
                    self.sample_rate,
                    self.buffer_size,
                    self.result_queue,
                    self.stop_event,
                ),
            )
            self.transcription_process.start()

            self.result_thread.start()

    def stop(self):
        self.stop_event.set()
        if self.transcription_process:
            self.transcription_process.join()
            self.transcription_process = None
        self.result_thread.join()
        self.input_queue.close()
        self.result_queue.close()

    def is_running(self):
        return (
            self.transcription_process is not None
            and self.transcription_process.is_alive()
        )

    def _result_loop(self):
        while not self.stop_event.is_set():
            if not self.result_queue.empty():
                result = self.result_queue.get()
                transcription, is_partial = result
                self.callback(transcription, is_partial)
            time.sleep(0.25)

    def _transcribe_loop(
        input_queue: mp.Queue,
        sample_rate: int,
        buffer_size: int,
        result_queue: mp.Queue,
        stop_event,
    ):
        log.info("Starting transcription process...")

        model = faster_whisper.WhisperModel(
            "small.en",
            device=os.environ["WHISPER_EXEC_BACKEND"],
            compute_type=os.environ["WHISPER_COMPUTE_TYPE"],
        )

        current_audio = np.array([])

        log.info("Model loaded. Transcription process started.")
        while not stop_event.is_set():
            any_audio_to_process = False

            if not input_queue.empty():
                any_audio_to_process = True

                # read from the queue into the current audio buffer
                while not input_queue.empty():
                    current_audio = np.append(current_audio, input_queue.get())

            if not any_audio_to_process:
                time.sleep(0.25)
                continue

            segments, _ = model.transcribe(current_audio, language="en", beam_size=5)

            is_partial = True

            if current_audio.size >= buffer_size:
                current_audio = np.array([])
                is_partial = False  # final transcription

            # concatenate segments and call the callback
            text = ""
            for segment in segments:
                text += segment.text + " "

            result_queue.put_nowait((text, is_partial))

            time.sleep(0.25)
