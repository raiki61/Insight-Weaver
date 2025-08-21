from typing import Union, List, Dict

from langchain_ollama import ChatOllama


class Client:
    """
    エージェントの高レベルな振る舞いを決定する司令塔です。

    設計:
        - 主な責務: アプリケーション全体の文脈を理解し、戦略的な判断を下すこと
        - 扱う情報: 会話が長くなりすぎてないか? 要約すべきか?
        - ループ検出: 同じ応答を繰り返していないか
        - 次の発話者: 次はAIが話すべきか、ユーザの入力を待つべきか
    """

    def __init__(self, ollama_base_url: str, model_name: str, temperature: float):
        self.base_url = ollama_base_url
        self.model_name = model_name
        self.temperature = temperature

    async def start_chat(self):
        ollama = ChatOllama(
            base_url=self.base_url, model=self.model_name, temperature=self.temperature
        )
        messages = [
            ("human", "やっほー。こんにちは。."),
        ]
        ai_msg = await ollama.ainvoke(messages)
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

    async def send_message_stream(self, contents: Union[str, List[Union[str, Dict]]]):
        if not self.chat:
            self.start_chat()

        pass
