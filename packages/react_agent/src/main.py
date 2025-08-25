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
        config=settings
    )
    client.initialize()

    # Clientからのストリームをasync forで受け取る
    user_prompt = "ヤッホー大阪KTです。たこ焼き愛するFJD. このネタ知ってますか"
    print(f"👤 User: {user_prompt}")
    print("\n🤖 AI:")

    response_stream =  client.send_message_stream(user_prompt)
    async for chunk in response_stream:
        print(chunk, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
