import os

import requests
import json
from experiments.models.base_client import BaseClient, Message


class QwenCompatClient(BaseClient):
    def __init__(self, model: str) -> None:
        self.model = model
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise Exception("❌ OPENROUTER_API_KEY not found in .env")
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def chat(self, messages: list[Message]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Role-Adherence-Experiment",
        }

        body = {"model": self.model, "messages": messages, "max_tokens": 200}

        response = requests.post(self.url, json=body, headers=headers)

        if response.status_code != 200:
            raise Exception(f"OpenRouter error {response.status_code}: {response.text}")

        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Ensure it returns a string
        if isinstance(content, list):
            content = str(content)
        
        return str(content)