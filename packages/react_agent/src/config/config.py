# config/config.py
from __future__ import annotations

from typing import Dict, List, Optional, Union, Annotated, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator

from .env_resolver import merge_safe_stdio_env

# ---- Model | Agent セクション ----------------------------------------------------------


class OllamaConfig(BaseModel):
    base_url: str
    model_name: str
    temperature: float = 0.0


class ChatCompressionConfig(BaseModel):
    context_percentage_threshold: float = 0.5


# ---- MCP セクション -------------------------------------------------------


class StdioServerConfig(BaseModel):
    transport: Literal["stdio"] = "stdio"
    command: str
    args: List[str] = []
    env: Optional[Dict[str, str]] = None


class StreamableHTTPServerConfig(BaseModel):
    transport: Literal["streamable_http"] = "streamable_http"
    url: HttpUrl
    headers: Optional[Dict[str, str]] = None


class SSEServerConfig(BaseModel):
    transport: Literal["sse"] = "sse"
    url: HttpUrl
    headers: Optional[Dict[str, str]] = None


MCPServerConfig = Annotated[
    Union[StdioServerConfig, StreamableHTTPServerConfig, SSEServerConfig],
    Field(discriminator="transport"),
]


class MCPServers(BaseModel):
    servers: Dict[str, MCPServerConfig] = Field(default_factory=dict)
    groups: Dict[str, List[str]] = Field(default_factory=dict)
    default_group: Optional[str] = None

    @field_validator("servers", mode="before")
    @classmethod
    def empty_servers_as_dict(cls, v):
        if v is None:
            return {}
        return v

    def resolve_active_group(self, env_var: str = "MCP_ACTIVE_GROUP") -> Optional[str]:
        import os

        return os.environ.get(env_var) or self.default_group

    def select(self, group: Optional[str] = None) -> Dict[str, MCPServerConfig]:
        if not group:
            return self.servers
        if group not in self.groups:
            raise KeyError(f"group not found: {group}. available={list(self.groups)}")
        names = self.groups[group]
        return {n: self.servers[n] for n in names if n in self.servers}

    def to_multiserver_dict(self, group: Optional[str] = None) -> Dict[str, dict]:
        out: Dict[str, dict] = {}
        for name, cfg in self.select(group).items():
            if isinstance(cfg, StdioServerConfig):
                item = {"transport": "stdio", "command": cfg.command, "args": cfg.args}
                merged = merge_safe_stdio_env(cfg.env)
                if merged:
                    item["env"] = merged
                out[name] = item
            else:
                item = {"transport": cfg.transport, "url": str(cfg.url)}
                if getattr(cfg, "headers", None):
                    item["headers"] = cfg.headers
                out[name] = item
        return out


# ---- 全体 Config -----------------------------------------------------------


class Config(BaseModel):
    ollama: OllamaConfig
    chat_compression: ChatCompressionConfig
    mcp_servers: Optional[MCPServers] = None