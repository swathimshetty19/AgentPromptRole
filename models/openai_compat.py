from typing import List, Dict
import requests, os
from dotenv import load_dotenv

# load environment variables from .env
load_dotenv()

class OpenAICompatClient:
    def __init__(self, model: str):
        self.model = model
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise Exception("❌ OPENROUTER_API_KEY not found in .env")
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def chat(self, messages: List[Dict[str, str]]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Role-Adherence-Experiment"
        }

        body = {"model": self.model, "messages": messages}

        response = requests.post(self.url, json=body, headers=headers)

        if response.status_code != 200:
            raise Exception(
                f"OpenRouter error {response.status_code}: {response.text}"
            )

        return response.json()["choices"][0]["message"]["content"]
