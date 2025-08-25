from dataclasses import dataclass


@dataclass
class ChatCompressInformation:
    original_token_count: int
    new_token_count: int