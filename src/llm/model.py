from llama_cpp import Llama


class LanguageModel:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LanguageModel, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "llm"):
            self.llm = Llama(
                model_path=R"C:\Users\roysh\Downloads\Llama-3.2-3B-Instruct-Q4_K_M.gguf",
                n_ctx=8192,
            )

    def generate_response(self, query):
        for chunk in self.llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "You are a note-taking assistant. Summarize the following note.",
                },
                {"role": "user", "content": query},
            ],
            stream=True,
        ):
            if "content" not in chunk["choices"][0]["delta"]:
                continue
            yield chunk["choices"][0]["delta"]["content"]
