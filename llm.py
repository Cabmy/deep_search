import ollama

MODEL = "qwen2.5"


def chat(prompt: str, system: str = "") -> str:
    """调用 Ollama 模型，返回文本响应"""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = ollama.chat(model=MODEL, messages=messages)
    return response["message"]["content"]
