from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    connections={
        #     途中
    }
)


class McpClient:
    """
    単一のMCPサーバクライアント。
    このクラスは、接続、からのツールの発見、および単一のMCPサーバーの状態の管理。
    """

    async def connect(self):
        """MCPサーバへの接続"""
        raise NotImplementedError

    async def discover(self):
        """MCPサーバからツールとプロンプトを発見する"""
        raise NotImplementedError

    async def disconnect(self):
        """MCPサーバとの接続を切断する"""
        raise NotImplementedError

    async def getStatus(self):
        """MCPサーバの状態を取得する"""
        raise NotImplementedError

    async def updateStatus(self):
        """MCPサーバのステータスを更新する"""
        raise NotImplementedError