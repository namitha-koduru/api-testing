from abc import ABC, abstractmethod

from flask import current_app


class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system: str = "") -> str:
        pass

    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        pass


class GeminiProvider(AIProvider):
    def __init__(self):
        import google.generativeai as genai

        genai.configure(api_key=current_app.config["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate(self, prompt: str, system: str = "") -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = self.model.generate_content(full_prompt)
        return response.text

    def chat(self, messages: list[dict]) -> str:
        history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})
        chat = self.model.start_chat(history=history)
        response = chat.send_message(messages[-1]["content"])
        return response.text


class OpenAIProvider(AIProvider):
    def __init__(self):
        from openai import OpenAI

        self.client = OpenAI(api_key=current_app.config["OPENAI_API_KEY"])

    def generate(self, prompt: str, system: str = "") -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages)

    def chat(self, messages: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=2048,
        )
        return response.choices[0].message.content


def get_ai_provider() -> AIProvider:
    provider = current_app.config.get("AI_PROVIDER", "gemini")
    if provider == "openai" and current_app.config.get("OPENAI_API_KEY"):
        return OpenAIProvider()
    if current_app.config.get("GEMINI_API_KEY"):
        return GeminiProvider()
    if current_app.config.get("OPENAI_API_KEY"):
        return OpenAIProvider()
    raise RuntimeError("No AI provider configured")
