import asyncio

from langchain_ollama import ChatOllama
from config.config_loader import settings


class Client:

    def __init__(self, ollama_base_url: str, model_name: str, temperature: str):
        self.base_url = ollama_base_url
        self.model_name = model_name
        self.temperature = temperature

    async def start_chat(self):
        ollama = ChatOllama(base_url=self.base_url, model=self.model_name, template=self.temperature)
        messages = [
            ("human", "やっほー。こんにちは。."),
        ]
        ai_msg = ollama.invoke(messages)
        print(ai_msg)
        pass

    async def initialize(self):
        pass

    async def add_history(self):
        pass

    def is_initialized(self):
        pass

    async def reset_chat(self):
        pass

    async def send_message_stream(self):
        pass


async def main():
    print("Hello from react-agent!")
    client = Client(ollama_base_url=settings.ollama.base_url, model_name=settings.ollama.model_name,
                    temperature=settings.ollama.temperature)
    await client.start_chat()


if __name__ == "__main__":
    asyncio.run(main())
