from fastapi import FastAPI

# 共有パッケージからインポートできているか確認
from common_types import __name__ as common_types_name

app = FastAPI()


@app.get("/")
def read_root():
    return {
        "message": "Backend is running!",
        "shared_package": f"Successfully imported: {common_types_name}",
    }
