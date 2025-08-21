from typing import Union, List, Dict, AsyncGenerator

from config.config import OllamaConfig
from core.chat import Chat


class Client:
    """
    エージェントの高レベルな振る舞いを決定する司令塔です。

    設計:
        - 主な責務: アプリケーション全体の文脈を理解し、戦略的な判断を下すこと
        - 扱う情報: 会話が長くなりすぎてないか? 要約すべきか?
        - ループ検出: 同じ応答を繰り返していないか
        - 次の発話者: 次はAIが話すべきか、ユーザの入力を待つべきか
    """

    def __init__(self, ollama_config: OllamaConfig):
        self.chat : Chat | None = None
        self.ollama_config = ollama_config

    def initialize(self):
        self.chat = self.start_chat()

    def reset_chat(self):
        self.chat = self.start_chat()

    def start_chat(self) -> Chat:
        return Chat(ollama_config=self.ollama_config, history=[])

    async def add_history(self):
        pass

    async def send_message_stream(
            self,
            contents: Union[str, List[Union[str, Dict]]]
    ) -> AsyncGenerator[str, None]:

        if not self.chat:
            self.chat = await self.start_chat()

        # awaitではなく、async forでストリームを中継する
        # Chatクラスからのトークンの流れを、そのまま呼び出し元に流す
        async for token in self.chat.send_message_stream(contents):
            yield token
