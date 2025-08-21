from pydantic import BaseModel


class OllamaConfig(BaseModel):
    base_url: str
    model_name: str
    temperature: float

class Config(BaseModel):
    ollama: OllamaConfig


