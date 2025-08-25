from pydantic import BaseModel


class OllamaConfig(BaseModel):
    base_url: str
    model_name: str
    temperature: float

class ChatCompressionConfig(BaseModel):
    context_percentage_threshold: float

class Config(BaseModel):
    # TODO test
    ollama: OllamaConfig
    chat_compression: ChatCompressionConfig
