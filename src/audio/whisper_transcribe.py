from simpler_whisper import whisper
import time
import numpy as np
import threading
import multiprocessing as mp
import os

if os.name == "nt":
    import multiprocessing.popen_spawn_win32 as forking
else:
    import multiprocessing.popen_fork as forking
import sys

from utils import resource_path


class _Popen(forking.Popen):
    def __init__(self, *args, **kw):
        if hasattr(sys, "frozen"):
            # We have to set original _MEIPASS2 value from sys._MEIPASS
            # to get --onefile mode working.
            os.putenv("_MEIPASS2", sys._MEIPASS)
        try:
            super(_Popen, self).__init__(*args, **kw)
        finally:
            if hasattr(sys, "frozen"):
                # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                # available. In those cases we cannot delete the variable
                # but only set it to the empty string. The bootloader
                # can handle this case.
                if hasattr(os, "unsetenv"):
                    os.unsetenv("_MEIPASS2")
                else:
                    os.putenv("_MEIPASS2", "")


class Process(mp.Process):
    _Popen = _Popen


def my_log_callback(level, message):
    pass


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
            self.transcription_process.join(timeout=5)
            if self.transcription_process.is_alive():
                self.transcription_process.terminate()
            self.transcription_process = None
        if self.result_thread:
            self.result_thread.join(timeout=5)
            self.result_thread = None
        if hasattr(self, "input_queue"):
            while not self.input_queue.empty():
                try:
                    self.input_queue.get_nowait()
                except:
                    pass
            self.input_queue.close()
            self.input_queue.join_thread()
        if hasattr(self, "result_queue"):
            while not self.result_queue.empty():
                try:
                    self.result_queue.get_nowait()
                except:
                    pass
            self.result_queue.close()
            self.result_queue.join_thread()

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
        whisper.set_log_callback(my_log_callback)

        model = whisper.load_model(
            resource_path.resource_path("data/ggml-small.en-q5_1.bin"),
            True,
        )

        current_audio = np.array([])

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

            text = model.transcribe(current_audio)

            is_partial = True

            if current_audio.size >= buffer_size:
                current_audio = np.array([])
                is_partial = False  # final transcription

            result_queue.put_nowait((text, is_partial))

            time.sleep(0.25)
