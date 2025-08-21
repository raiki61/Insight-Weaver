from typing import Sequence, AsyncGenerator, List

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from tenacity import stop_after_attempt, wait_random_exponential

from config.config import OllamaConfig


class Chat:
    """
    APIとの低レベルな通信に特化したクラス
    設計:
        - 主な責務: 指示された内容を、技術的に正しくAPIに送信し、応答を受け取ること
        - 扱う情報:
            - 会話履歴: `user`と`model`のターンが正しく交互になっているか
            - API応答: レスポンスは有効であるか、エラーは無いか
    """

    def __init__(self, ollama_config: OllamaConfig, history: Sequence[BaseMessage] = None):
        """
        :param ollama_config: Ollamaの設定
        :param history: 初期化時の会話履歴
        """
        self.config = ollama_config
        self.history: List[BaseMessage] = list(history) if history else []

        # ChatOllamaインスタンスを生成し、リトライ処理を追加
        # ネットワークエラーなどで最大3回まで、ランダムな待ち時間で再試行する
        self.chat = ChatOllama(
            temperature=ollama_config.temperature,
            base_url=ollama_config.base_url,
            model=ollama_config.model_name
        )
    def send_message(self, message: str) -> BaseMessage:
        """メッセージを送信し、完全な応答を一度に受け取る（同期的）"""

        # 新しいユーザーメッセージを履歴に追加
        user_message = HumanMessage(content=message)
        self.history.append(user_message)

        # 履歴全体を渡してAPIを呼び出し
        ai_response = self.chat.invoke(self.history)

        # AIの応答を履歴に追加
        self.history.append(ai_response)

        return ai_response

    async def send_message_stream(self, message: str) -> AsyncGenerator[str, None]:
        """メッセージを送信し、応答をストリーミングで受け取る（非同期）"""

        # 新しいユーザーメッセージを履歴に追加
        user_message = HumanMessage(content=message)
        self.history.append(user_message)

        full_response_content = ""
        # 履歴全体をストリーミングAPIに渡す
        async for chunk in self.chat.astream(self.history):
            # chunk.content が文字列の塊
            yield chunk.content
            full_response_content += chunk.content

        # ストリーミング完了後、完全な応答をAIメッセージとして履歴に追加
        ai_message = AIMessage(content=full_response_content)
        self.history.append(ai_message)

    def get_history(self) -> List[BaseMessage]:
        """現在の会話履歴を返す"""
        return self.history
