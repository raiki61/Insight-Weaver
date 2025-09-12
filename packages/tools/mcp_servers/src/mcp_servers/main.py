from mcp.server.fastmcp import FastMCP
from pydantic import Field, BaseModel

mcp = FastMCP("Sample")

@mcp.tool()
def get_server_status() -> dict[str, str]:
    """Get the current status of the server."""
    return {"status": "ok"}

@mcp.tool()
def start_server() -> dict[str, str]:
    """Start the server."""
    return {"status": "Server start"}

@mcp.tool()
def add(a: int, b: int) -> dict[str, int]:
    """Add two numbers."""
    return {"result": a + b}


@mcp.tool()
def get_internal_server_log(lines: int = 5, log_level: str = "INFO") -> dict[str, list[str]]:
    """
    Retrieves the last N lines from this application's internal log file.
    This is the ONLY way to check for internal errors or specific operational messages.
    Use this tool to diagnose problems or check the application's health.
    """
    # 実際にはここでログファイルを読み込む処理を書くが、今回はダミーのログを生成する
    print(f"--- Tool Executing: get_internal_server_log(lines={lines}, log_level='{log_level}') ---")

    dummy_logs = [
        "[INFO] 2025-09-12 17:20:01 - Server startup complete.",
        "[INFO] 2025-09-12 17:22:34 - User 'admin' logged in.",
        "[WARNING] 2025-09-12 17:23:05 - Disk space is running low (85% usage).",
        "[INFO] 2025-09-12 17:25:11 - Received request for /api/data.",
        "[ERROR] 2025-09-12 17:26:47 - Database connection failed: Timeout expired.",
        "[INFO] 2025-09-12 17:28:00 - User 'guest' logged in."
    ]

    # log_levelでフィルタリングし、指定された行数を返す
    filtered_logs = [log for log in dummy_logs if f"[{log_level.upper()}]" in log]

    return {"log_entries": filtered_logs[-lines:]}


import io
from contextlib import redirect_stdout


# --- これまでのツール定義は一旦すべてコメントアウトするか削除 ---

# --- 新しい究極のツールの定義 ---
@mcp.tool()
def python_repl(code: str) -> dict[str, str]:
    """
    Executes a string of Python code and returns its standard output.
    Use this for ANY calculations, file operations, or data manipulation.
    The code will be executed in an environment where it can call other functions
    defined on the server, such as 'read_log_file()'.
    """

    # ログを読み取るためのヘルパー関数をここで定義（モデルから呼び出せるようにする）
    def read_log_file(lines: int, log_level: str) -> list[str]:
        # 以前のツールからロジックを拝借
        dummy_logs = [
            "[INFO] 2025-09-12 17:20:01 - Server startup complete.",
            "[WARNING] 2025-09-12 17:23:05 - Disk space is running low (85% usage).",
            "[ERROR] 2025-09-12 17:26:47 - Database connection failed: Timeout expired.",
            "[INFO] 2025-09-12 17:28:00 - User 'guest' logged in."
        ]
        filtered_logs = [log for log in dummy_logs if f"[{log_level.upper()}]" in log]
        return filtered_logs[-lines:]

    # Pythonコードを実行するための環境を準備
    # モデルが 'read_log_file' 関数を呼び出せるように渡す
    execution_globals = {"read_log_file": read_log_file}

    # 標準出力をキャプチャするためのバッファ
    buffer = io.StringIO()

    try:
        with redirect_stdout(buffer):
            exec(code, execution_globals)
        output = buffer.getvalue()
        # 出力がなければ成功メッセージを返す
        if not output:
            output = "Code executed successfully with no output."
        return {"output": output}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run(transport = "streamable-http")
