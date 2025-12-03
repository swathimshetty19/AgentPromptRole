import os

import requests
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from experiments.models.base_client import BaseClient, Message


class ChatOpenAICompatClient(BaseClient):
    def __init__(self, model: str) -> None:
        # For OpenRouter, use "openai/model-name" format
        if model.startswith("chatopenai/"):
            self.model = "openai/" + model.split("/")[-1]
        else:
            self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise Exception("❌ OPENAI_API_KEY not found in .env")
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

        return response.json()["choices"][0]["message"]["content"]
