from abc import ABC


class ChatCompressInformation(ABC):
    original_token_count: int
    new_token_count: int