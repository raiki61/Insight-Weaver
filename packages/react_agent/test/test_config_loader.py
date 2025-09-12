# tests/test_config_loader.py
import os
from pathlib import Path

import pytest

from config.config_loader import load_config


def write_file(p: Path, content: str):
    p.write_text(content, encoding="utf-8")


def test_load_config_env_and_dotenv_precedence(tmp_path, monkeypatch):
    """
    .env と OS 環境の優先順位を検証:
    - override_env=False: OS > .env
    - override_env=True : .env が OS を上書き
    """
    # --- 1) 準備（.env と YAML） ---
    dotenv = tmp_path / ".env"
    yaml_path = tmp_path / "config.yaml"

    write_file(
        dotenv,
        "\n".join(
            [
                "HOST=dotenv-host",
                "PORT=18000",
                "WEATHER_TOKEN=from_dotenv",
                "PLAIN_HOST=dotenv-plain",
            ]
        ),
    )

    write_file(
        yaml_path,
        """
ollama:
  base_url: ${OLLAMA_URL}
  model_name: llama3
  temperature: 0.3

chat_compression:
  context_percentage_threshold: 0.5

mcp_servers:
  servers:
    math:
      transport: stdio
      command: python
      args:
        - "~/project/tools/math_server.py"
      env:
        PYTHONUNBUFFERED: "1"

    weather:
      transport: streamable_http
      url: "http://${HOST}:${PORT}/mcp/"
      headers:
        Authorization: "Bearer ${WEATHER_TOKEN:-dev-token}"

    sse_search:
      transport: sse
      url: "http://$PLAIN_HOST/mcp/"
  default_group: core
  groups:
    core: [math, weather]
""",
    )

    # --- 2) OS 環境を設定（OS > .env を確かめるため） ---
    monkeypatch.setenv("OLLAMA_URL", "http://localhost:11434")
    monkeypatch.setenv("HOST", "os-host")
    monkeypatch.setenv("PORT", "8000")
    # WEATHER_TOKEN は未設定にしておき、デフォルト展開も別テストで確認
    monkeypatch.setenv("PLAIN_HOST", "os-plain")

    # --- 3) override_env=False（既定）: OS > .env ---
    cfg = load_config(str(yaml_path), dotenv_path=str(dotenv), override_env=False)

    # weather.url に OS 側の HOST/PORT が反映される
    weather = cfg.mcp_servers.servers["weather"]
    assert str(weather.url) == "http://os-host:8000/mcp/"

    # sse_search.url は $PLAIN_HOST の展開（os-plain）
    sse = cfg.mcp_servers.servers["sse_search"]
    assert str(sse.url) == "http://os-plain/mcp/"

    # --- 4) override_env=True: .env が OS を上書き ---
    cfg2 = load_config(str(yaml_path), dotenv_path=str(dotenv), override_env=True)
    weather2 = cfg2.mcp_servers.servers["weather"]
    assert str(weather2.url) == "http://dotenv-host:18000/mcp/"
    sse2 = cfg2.mcp_servers.servers["sse_search"]
    assert str(sse2.url) == "http://dotenv-plain/mcp/"


def test_load_config_default_substitution_and_partial_string(tmp_path, monkeypatch):
    """
    - ${VAR:-default} のデフォルト値展開
    - "Bearer ${TOKEN}" のような部分文字列置換
    """
    yaml_path = tmp_path / "config.yaml"
    write_file(
        yaml_path,
        """
ollama:
  base_url: http://localhost:11434
  model_name: llama3
  temperature: 0.2

chat_compression:
  context_percentage_threshold: 0.35

mcp_servers:
  servers:
    weather:
      transport: streamable_http
      url: "http://localhost:8000/mcp/"
      headers:
        Authorization: "Bearer ${WEATHER_TOKEN:-dev-token}"
""",
    )

    # 実行前に環境変数をクリア
    monkeypatch.delenv("WEATHER_TOKEN", raising=False)

    cfg = load_config(str(yaml_path), strict_env=True)
    weather = cfg.mcp_servers.servers["weather"]
    # 未設定なのでデフォルト "dev-token" が使われる
    assert weather.headers["Authorization"] == "Bearer dev-token"

    # TOKEN を設定すれば置換される（部分文字列）
    monkeypatch.setenv("WEATHER_TOKEN", "abc123")
    cfg2 = load_config(str(yaml_path), strict_env=True)
    weather2 = cfg2.mcp_servers.servers["weather"]
    assert weather2.headers["Authorization"] == "Bearer abc123"


def test_load_config_strict_env_missing_raises(tmp_path, monkeypatch):
    """
    strict_env=True のとき、未定義の ${VAR} があれば例外を投げる
    """
    yaml_path = tmp_path / "config.yaml"
    write_file(
        yaml_path,
        """
ollama:
  base_url: ${MISSING_BASE_URL}
  model_name: llama3
  temperature: 0.1

chat_compression:
  context_percentage_threshold: 0.5

mcp_servers:
  servers: {}
""",
    )

    with pytest.raises(ValueError) as ei:
        load_config(str(yaml_path), strict_env=True)
    assert "MISSING_BASE_URL" in str(ei.value)


def test_load_config_home_and_plain_dollar_expansion(tmp_path, monkeypatch):
    """
    ~（ホーム）と $VAR の展開を検証
    """
    yaml_path = tmp_path / "config.yaml"
    write_file(
        yaml_path,
        """
ollama:
  base_url: http://localhost:11434
  model_name: llama3
  temperature: 0.2

chat_compression:
  context_percentage_threshold: 0.5

mcp_servers:
  servers:
    math:
      transport: stdio
      command: python
      args:
        - "~/project/math_server.py"
      env: {}
    remote:
      transport: streamable_http
      url: "http://$REMOTE_HOST:$REMOTE_PORT/mcp/"
""",
    )

    monkeypatch.setenv("REMOTE_HOST", "r.example.com")
    monkeypatch.setenv("REMOTE_PORT", "3000")

    cfg = load_config(str(yaml_path))
    math = cfg.mcp_servers.servers["math"]
    # ~ が展開されていること
    assert os.path.expanduser("~/project/math_server.py") in math.args[0]

    remote = cfg.mcp_servers.servers["remote"]
    assert str(remote.url) == "http://r.example.com:3000/mcp/"


def test_to_multiserver_dict_safe_env_merge_for_stdio(tmp_path, monkeypatch):
    """
    MCPServers.to_multiserver_dict() 実行時に、
    stdio の env が安全な既定環境（PATH 等）とマージされることを確認。
    """
    yaml_path = tmp_path / "config.yaml"
    write_file(
        yaml_path,
        """
ollama:
  base_url: http://localhost:11434
  model_name: llama3
  temperature: 0.2

chat_compression:
  context_percentage_threshold: 0.5

mcp_servers:
  servers:
    math:
      transport: stdio
      command: python
      args: ["script.py"]
      env:
        MY_FLAG: "1"
    weather:
      transport: streamable_http
      url: "http://localhost:8000/mcp/"
  default_group: core
  groups:
    core: [math, weather]
""",
    )

    cfg = load_config(str(yaml_path))
    ms_dict = cfg.mcp_servers.to_multiserver_dict("core")

    # stdio 側：env が存在し、PATH 等が残っている（環境によってキー名は大小混在する可能性あり）
    stdio_env = ms_dict["math"].get("env", {})
    assert stdio_env.get("MY_FLAG") == "1"
    assert any(k.upper() == "PATH" for k in stdio_env.keys())

    # http 側：headers が未指定なら含まれない
    assert "headers" not in ms_dict["weather"]
    assert ms_dict["weather"]["url"] == "http://localhost:8000/mcp/"
