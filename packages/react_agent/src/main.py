import asyncio
from pathlib import Path

from config.config_loader import load_config
from core.client import Client


async def main():
    print("Hello from react-agent!")

    # 1. プログラムの実行開始点で設定ファイルのパスを決定する
    config_path = Path(__file__).parent.parent / "config.yml"

    # 2. 設定を明示的に読み込む
    settings = load_config(str(config_path))

    client = Client(
        ollama_base_url=settings.ollama.base_url,
        model_name=settings.ollama.model_name,
        temperature=settings.ollama.temperature,
    )
    await client.start_chat()


if __name__ == "__main__":
    asyncio.run(main())
