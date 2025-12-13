import os

import requests
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from experiments.models.base_client import BaseClient, Message


class ChatOpenAICompatClient(BaseClient):
    def __init__(self, model: str) -> None:
        self.model = model.split("/")[-1]
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise Exception("❌ OPENAI_API_KEY not found in .env")
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def chat(self, messages) -> str:
        try:
            model = ChatOpenAI(model=self.model, temperature=0.0)

            messages_prompt = []
            for message_dict in messages:
                if message_dict["role"] == "system":
                    messages_prompt.append(
                        SystemMessage(content=message_dict["content"])
                    )
                elif message_dict["role"] == "user":
                    messages_prompt.append(
                        HumanMessage(content=message_dict["content"])
                    )
                elif message_dict["role"] == "assistant":
                    messages_prompt.append(AIMessage(content=message_dict["content"]))

            chat_prompt = ChatPromptTemplate.from_messages(messages_prompt)
            chain = chat_prompt | model | StrOutputParser()
            response = chain.invoke({})
            return response.strip()

        except Exception as e:
            print(f"An error occurred during LangChain API call: {e}")
            return f'{{"error": "API call failed: {str(e)}"}}'