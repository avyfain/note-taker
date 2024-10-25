from llama_cpp import Llama, llama_log_set
import ctypes
from utils.storage import fetch_data
from utils.defaults import default_prompt, default_model, default_model_file


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
            # log_callback = ctypes.CFUNCTYPE(
            #     None, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p
            # )(my_log_callback)
            # llama_log_set(log_callback, ctypes.c_void_p())
            self.llm = Llama.from_pretrained(
                repo_id=fetch_data("settings.json", "model", default_model),
                filename=fetch_data("settings.json", "model_file", default_model_file),
                verbose=True,
                n_ctx=8192,
            )

    def generate_response(self, query):
        for chunk in self.llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": fetch_data("settings.json", "prompt", default_prompt),
                },
                {"role": "user", "content": query},
            ],
            stream=True,
        ):
            if "content" not in chunk["choices"][0]["delta"]:
                continue
            yield chunk["choices"][0]["delta"]["content"]
