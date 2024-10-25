import threading
from simpler_whisper.whisper import ThreadedWhisperModel
from utils import resource_path


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
        self.model = ThreadedWhisperModel(
            model_path=model_path,
            callback=self.handle_result,
            use_gpu=True,
            max_duration_sec=10.0,
        )
        self.callback = None

    def handle_result(self, chunk_id: int, text: str, is_partial: bool):
        if self.callback:
            self.callback(chunk_id, text, is_partial)

    def start(self, callback=None):
        if callback:
            self.callback = callback
        self.model.start()

    def stop(self):
        self.model.stop()

    def queue_audio(self, audio_chunk):
        self.model.queue_audio(audio_chunk)
