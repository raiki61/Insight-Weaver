from pydantic import BaseModel


class OllamaConfig(BaseModel):
    base_url:str
    model_name:str
    temperature:str

class Config(BaseModel):
    ollama: OllamaConfig


