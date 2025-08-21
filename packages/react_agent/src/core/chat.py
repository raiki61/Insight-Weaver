from typing import Sequence, Any

from langchain_core.messages import BaseMessage
from langchain_core.prompt_values import PromptValue
from langchain_ollama import ChatOllama

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

    def __init__(self, ollama_config: OllamaConfig, history: PromptValue | str | Sequence[
        BaseMessage | list[str] | tuple[str, str] | str | dict[str, Any]]):
        """
        TODO ollama以外のプロバイダー対応
        :param ollama_config:
        :param history:
        """
        self.config = ollama_config
        self.history = history
        self.chat = ChatOllama(temperature=ollama_config.temperature, base_url=ollama_config.base_url, model=OllamaConfig.model_name)

    async def send_message(self, prompt_id: str):
        pass

    async def send_message_stream(self, prompt_id: str):
        """
        1. 渡された会話履歴を使って、実際にAPIへのリクエストを送信します。
        2. APIからの応答をストリーミングで受け取ります。
        3. 通信エラーが発生した場合のリトライを処理します。
        4. 受け取った応答を整形し、履歴に追加します。
        :param prompt_id:
        :return:
        """
        pass
