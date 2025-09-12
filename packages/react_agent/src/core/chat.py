import copy
from typing import Sequence, AsyncGenerator, List

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama

from config.config import OllamaConfig
from tools.tool_registry import ToolRegistry


def is_valid_message(message: BaseMessage) -> bool:
    """
    モデルからの応答であるAIMessageが有効かどうかを判定する。
    HumanMessageなどは常に有効とみなす。
    """
    # AIMessageでなければ、常に有効（ユーザー入力などは検証不要）
    if not isinstance(message, AIMessage):
        return True

    # AIMessageの場合、content属性が存在し、かつ空文字列でないことを確認
    # bool(message.content) は None や "" の場合に False になる
    return bool(message.content and isinstance(message.content, str))


def extract_curated_history(
    comprehensive_history: List[BaseMessage],
) -> List[BaseMessage]:
    """
    完全な履歴から、モデルへの入力に適した有効な履歴（curated history）を抽出する。

    モデルが無効な応答（安全フィルターなど）を返した場合、その応答と、それを引き起こした直前のユーザー入力を履歴から除外する。
    :param comprehensive_history:
    :return:
    """
    if not comprehensive_history:
        return []

    curated_history: List[BaseMessage] = []
    i = 0
    length = len(comprehensive_history)

    while i < length:
        current_message = comprehensive_history[i]
        # ユーザのターンはそのまま追加
        if isinstance(current_message, HumanMessage):
            curated_history.append(comprehensive_history[i])
            i += 1
        else:
            model_output: List[BaseMessage] = []
            is_valid_turn = True

            while i < length and isinstance(comprehensive_history[i], AIMessage):
                current_message = comprehensive_history[i]
                model_output.append(current_message)
                if not is_valid_message(current_message):
                    is_valid_turn = False
                i += 1

            if is_valid_turn:
                curated_history.extend(model_output)
            else:
                if curated_history:
                    curated_history.pop()

    return curated_history


class Chat:
    """
    APIとの低レベルな通信に特化したクラス
    設計:
        - 主な責務: 指示された内容を、技術的に正しくAPIに送信し、応答を受け取ること
        - 扱う情報:
            - 会話履歴: `user`と`model`のターンが正しく交互になっているか
            - API応答: レスポンスは有効であるか、エラーは無いか
    """

    def __init__(
        self, ollama_config: OllamaConfig, history: Sequence[BaseMessage] = None, tool_registry: ToolRegistry = None
    ):
        """
        :param ollama_config: Ollamaの設定
        :param history: 初期化時の会話履歴
        """
        self.config = ollama_config
        self.history: List[BaseMessage] = list(history) if history else []
        self.tool_registry = tool_registry

        # ChatOllamaインスタンスを生成し、リトライ処理を追加
        # ネットワークエラーなどで最大3回まで、ランダムな待ち時間で再試行する
        self.chat = ChatOllama(
            temperature=ollama_config.temperature,
            base_url=ollama_config.base_url,
            model=ollama_config.model_name,
            # reasoning=True,
        )
        if tool_registry is not None:
            self.chat = self.chat.bind_tools(tools=self.tool_registry.get_all_tools())

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

    def get_history(self, curated: bool = False) -> List[BaseMessage]:
        if curated:
            history = extract_curated_history(self.history)
        else:
            history = self.history

        return copy.deepcopy(history)

    def add_history(self, message: BaseMessage):
        self.history.append(message)

    def set_history(self, history: List[BaseMessage]):
        self.history = history

    def count_tokens(self, messages: List[BaseMessage]) -> int:
        # TODO 責務としてここでよいのか

        # TODO これちゃんと計算出来てるか怪しいので確認が必要
        return self.chat.get_num_tokens_from_messages(messages)

    def token_limit(self):
        # TODO 責務としてここでよいのか

        # TODO: モデルごとのトークン上限を取得する実装が必要です。
        raise NotImplementedError("token_limit is not yet implemented.")
