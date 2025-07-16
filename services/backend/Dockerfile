# services/backend/Dockerfile

# ベースイメージとして軽量なpython:3.11-slimを使用
FROM python:3.11-slim

# --- 環境変数の設定 ---
# Pythonのログがバッファリングされず、コンテナのログとしてすぐに出力されるようにします。
ENV PYTHONUNBUFFERED 1
# Pythonが.pycファイル（バイトコードキャッシュ）を生成しないようにします。
ENV PYTHONDONTWRITEBYTECODE 1

# --- 作業ディレクトリの設定 ---
WORKDIR /app

# --- 依存関係のインストール ---
# 1. 依存関係の定義ファイルを先にコピーします。
#    この層は頻繁に変更されないため、Dockerのキャッシュが効きやすくなります。
COPY ./packages /app/packages
COPY ./services/backend/requirements.txt .

# 2. 依存関係をインストールします。
#    まず requirements.txt に記載されたライブラリをインストールし、
#    次にローカルの共有パッケージをインストールします。
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir ./packages/common_types

# --- アプリケーションコードのコピー ---
# 3. アプリケーションのソースコードをコピーします。
#    この層は頻繁に変更されることを想定しています。
COPY ./services/backend /app/services/backend

# 4. PYTHONPATHを設定します。
#    これにより、Pythonがモジュールを探すパスにプロジェクトのルート(/app)が追加され、
#    `services.backend.main` のようなインポートが安定して解決されるようになります。
ENV PYTHONPATH "${PYTHONPATH}:/app"

# --- コンテナ起動コマンド ---
# 5. uvicornサーバーを起動します。
#    コンテナ外部からアクセスできるように、ホストを 0.0.0.0 に設定します。
CMD ["uvicorn", "services.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
