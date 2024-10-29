import threading
from simpler_whisper.whisper import (
    ThreadedWhisperModel,
    set_log_callback,
    WhisperSegment,
)
from utils import resource_path
import platform
from typing import Callable, List


def my_log_callback(level, message):
    # prevent debug messages from being printed
    pass


class Transcriber:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Transcriber, cls).__new__(cls)
                    cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self):
        model_path = resource_path.resource_path("data/ggml-small.en-q5_1.bin")
        use_gpu = not (platform.system() == "Darwin")
        self.model = ThreadedWhisperModel(
            model_path=model_path,
            callback=self.handle_result,
            use_gpu=use_gpu,
            max_duration_sec=10.0,
        )
        set_log_callback(my_log_callback)
        self.callback = None

    def handle_result(
        self, chunk_id: int, text: List[WhisperSegment], is_partial: bool
    ):
        if self.callback:
            self.callback(chunk_id, text, is_partial)

    def start(self, callback: Callable[[int, List[WhisperSegment], bool], None] = None):
        if callback:
            self.callback = callback
        self.model.start()

    def stop(self):
        self.model.stop()

    def queue_audio(self, audio_chunk):
        self.model.queue_audio(audio_chunk)
