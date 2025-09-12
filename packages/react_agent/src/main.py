import asyncio
from pathlib import Path

from config.config_loader import load_config
from core.client import Client
from tools.tool_discoverer import ToolDiscoverer
from tools.tool_registry import ToolRegistry
from tools.tool_registry_factory import ToolRegistryFactory
from langchain_core.globals import set_debug, set_verbose

set_debug(True)
set_verbose(True)


async def main():
    print("Hello from react-agent!")

    # 1. プログラムの実行開始点で設定ファイルのパスを決定する
    config_path = Path(__file__).parent.parent / "config.yml"

    # 2. 設定を明示的に読み込む
    settings = load_config(str(config_path))

    tool_registry_factory = ToolRegistryFactory(tool_discoverer=ToolDiscoverer(settings.mcp_servers))
    tool_registry: ToolRegistry = await tool_registry_factory.create()

    client = Client(config=settings, tool_registry=tool_registry)
    client.initialize()

    # Clientからのストリームをasync forで受け取る
    user_prompt = "最新のINFOレベルのログを2件だけ見せてください。"
    print(f"👤 User: {user_prompt}")
    print("\n🤖 AI:")

    response_stream = client.send_message_stream(user_prompt)
    async for chunk in response_stream:
        print(chunk, end="", flush=True)
    print()

if __name__ == "__main__":
    asyncio.run(main())
