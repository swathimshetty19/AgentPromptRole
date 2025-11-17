import os

import requests

from experiments.models.base_client import BaseClient, Message


class QwenCompatClient(BaseClient):
    def __init__(self, model: str) -> None:
        self.model = model
        self.api_key = os.getenv("QWEN_API_KEY")
        if not self.api_key:
            raise Exception("❌ QWEN_API_KEY not found in .env")
        self.url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    def chat(self, messages: list[Message]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        body = {"model": self.model, "messages": messages}

        response = requests.post(self.url, json=body, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Qwen API error {response.status_code}: {response.text}")

        return response.json()["choices"][0]["message"]["content"]