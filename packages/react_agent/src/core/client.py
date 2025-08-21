from typing import Union, List, Dict, AsyncGenerator, Optional

from langchain_core.messages import BaseMessage

from config.config import Config
from core.chat import Chat
from core.turn import ChatCompressInformation

COMPRESSION_TOKEN_THRESHOLD = 0.7


def find_index_after_fraction(history: List[BaseMessage], fraction: float) -> int:
    """
    BaseMessageのリストで構成される履歴全体の文字数に対する
    指定された割合(fraction)を超えた直後のメッセージのインデックスを返す。
    """
    if not (0 < fraction < 1):
        raise ValueError("fractionは0より大きく1未満である必要があります。")

    if not history:
        return 0

    content_lengths = [len(message.model_dump_json()) for message in history]

    total_characters = sum(content_lengths)
    target_characters = total_characters * fraction

    characters_so_far = 0
    for i, length in enumerate(content_lengths):
        characters_so_far += length
        if characters_so_far >= target_characters:
            return i

    return len(content_lengths)


class Client:
    """
    エージェントの高レベルな振る舞いを決定する司令塔です。

    設計:
        - 主な責務: アプリケーション全体の文脈を理解し、戦略的な判断を下すこと
        - 扱う情報: 会話が長くなりすぎてないか? 要約すべきか?
        - ループ検出: 同じ応答を繰り返していないか
        - 次の発話者: 次はAIが話すべきか、ユーザの入力を待つべきか
    """

    def __init__(self, config: Config):
        self.chat : Chat | None = None
        self.ollama_config = config.ollama
        self.chat_compression_config = config.chat_compression

    def get_chat(self) -> Chat:
        if not self.chat:
            raise ValueError("Chat not initialized.")
        return self.chat

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
            self.chat = self.start_chat()

        # awaitではなく、async forでストリームを中継する
        # Chatクラスからのトークンの流れを、そのまま呼び出し元に流す
        async for token in self.chat.send_message_stream(contents):
            yield token

    async def try_compress_chat(self, prompt_id: str, force: bool) -> Optional[ChatCompressInformation]:
        curated_history = self.get_chat().get_history(True)

        if len(curated_history) == 0:
            return None

        model: str = self.ollama_config.model_name
        total_tokens = self.chat.count_tokens(curated_history)

        # FIXME ここでtoken計算できない場合などは、警告出したほうが良さそう

        context_percentage_threshold = self.chat_compression_config.context_percentage_threshold
        if not force:
            threshold = (
                context_percentage_threshold
                if context_percentage_threshold is not None
                else COMPRESSION_TOKEN_THRESHOLD
            )

            token_limit = 128000 # TODO token_limit(model)
            if total_tokens < threshold * token_limit:
                print("Token count is under the threshold. No compression needed.")
                return None

        # TODO 続き
        return True
