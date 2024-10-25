from llama_cpp import Llama, llama_log_set
import ctypes


def my_log_callback(level, message, user_data):
    pass


class LanguageModel:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LanguageModel, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "llm"):
            log_callback = ctypes.CFUNCTYPE(
                None, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p
            )(my_log_callback)
            llama_log_set(log_callback, ctypes.c_void_p())
            self.llm = Llama.from_pretrained(
                repo_id="bartowski/Llama-3.2-1B-Instruct-GGUF",
                filename="Llama-3.2-1B-Instruct-Q4_K_M.gguf",
                verbose=True,
                n_ctx=8192,
            )

    def generate_response(self, query):
        for chunk in self.llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a note-taking assistant. The following note has "
                        "user-typed section on top and potentially a transcription. "
                        "Summarize the note combining the user notes with the transcription."
                    ),
                },
                {"role": "user", "content": query},
            ],
            stream=True,
        ):
            if "content" not in chunk["choices"][0]["delta"]:
                continue
            yield chunk["choices"][0]["delta"]["content"]
