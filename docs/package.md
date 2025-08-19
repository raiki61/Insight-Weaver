はい、承知いたしました。
これまでの議論をすべて統合し、チームの誰もが参照できる網羅的なMarkdownドキュメントとして再構成します。

-----

# Python現代開発戦略：モノレポ構成による堅牢なアプリケーション設計

このドキュメントは、我々のチームが採用するPythonプロジェクトの標準的な設計思想と構成、そしてその運用方法をまとめたものです。この戦略の目的は、**メンテナンス性・拡張性・開発効率**を最大化し、高品質なソフトウェアを継続的に提供することです。

## 🍱 思想：一つの弁当箱、仕切られたおかず

我々のプロジェクトは、\*\*「一つの弁当箱（モノレポ）」\*\*として捉えます。関連するすべてのコード（API, CLI, ライブラリ）を一つのリポジトリで管理します。

しかし、その中身は\*\*「仕切られたおかず（独立したパッケージ）」\*\*のように、各コンポーネントが明確に分離されています。これにより、お互いが不用意に混ざり合うことなく、それぞれの役割に集中できます。

-----

## 🏛️ プロジェクトの全体構造 (`ProjectPhoenix` 例)

```
project-phoenix/
├── .venv/                 # 👈 プロジェクト唯一の仮想環境
├── .gitignore
├── uv.lock                # 👈 プロジェクト唯一のロックファイル
├── pyproject.toml         # 👈 プロジェクト全体の設定 (uv, Ruffなど)
├── README.md              # 👈 プロジェクト全体の目的・セットアップ方法
│
└── packages/              # 🍱 ここが弁当箱の中身（各コンポーネント）
    │
    ├── phoenix-core/      # 🧠 [コア部品] ビジネスロジック・ライブラリ
    │   ├── pyproject.toml     # 'phoenix-core' パッケージの定義
    │   └── src/phoenix_core/
    │
    ├── phoenix-cli/       # 📦 [製品1] CLIアプリケーション
    │   ├── pyproject.toml     # 'phoenix-cli' パッケージの定義
    │   └── src/phoenix_cli/
    │
    └── phoenix-api/       # 📦 [製品2] Web APIアプリケーション
        ├── pyproject.toml     # 'phoenix-api' パッケージの定義
        └── src/phoenix_api/
```

### 各コンポーネントの役割

  * **`phoenix-core` (頭脳 🧠)**
      * プロジェクトの心臓部。ビジネスロジック、データモデルなど、アプリケーションの本質的な機能だけを持つ純粋なライブラリです。
      * **どのように使われるかを知りません。**
  * **`phoenix-cli`, `phoenix-api` (インターフェース 📦)**
      * `core`を操作するための「製品」です。ユーザーからの入力を受け取り、`core`に処理を依頼し、結果を返します。
      * **ビジネスロジックを持ちません。**

-----

## 🛠️ 開発環境のセットアップ

このモノレポ開発を効率的に行うため、環境は**プロジェクトルートに一つだけ**作ります。

### 1\. 仮想環境の作成と有効化

プロジェクトのルートディレクトリで、`venv`を一つだけ作成します。

```bash
# 仮想環境を作成 (.venvという名前が標準)
$ python -m venv .venv

# 有効化 (macOS / Linux)
$ source .venv/bin/activate

# 有効化 (Windows)
> .venv\Scripts\activate
```

### 2\. `.gitignore`の設定

作成した`.venv`がGitリポジトリに含まれないよう、`.gitignore`に必ず追加します。

```gitignore
# .gitignore
.venv/
```

### 3\. 依存関係のインストール (ワークスペース利用)

`uv`のようなモダンなツールを使い、すべてのパッケージを一度に管理します。

まず、ルートの`pyproject.toml`に、管理対象のパッケージがどこにあるかを教えます。

**`/pyproject.toml`**

```toml
# 開発ツール全体の設定
[tool.ruff]
# ...

# uvにワークスペースの場所を教える
[tool.uv.workspaces]
members = ["packages/*"]
```

次に、`uv sync`コマンドで、`packages/`配下のすべてのパッケージを**編集可能モード**でインストールします。

```bash
(.venv) $ uv sync
```

`uv`は、`core`, `cli`, `api`それぞれの`pyproject.toml`を読み込み、必要な依存関係をすべてこの単一の`.venv`内にインストールしてくれます。

-----

## 🚀 日々の開発ワークフロー

### ロジックの変更と即時確認

`venv`が一つなので、`phoenix-core`のコードを一行変更するだけで、その影響が`phoenix-cli`や`phoenix-api`に**即座に反映されます**。これがこの構成の最大の強みです。

```bash
# 1. ターミナル1でAPIサーバーを起動
(.venv) $ uvicorn phoenix_api.main:app --reload

# 2. VSCodeなどで phoenix-core/src/phoenix_core/logic.py を編集・保存

# 3. サーバーが自動でリロードされ、変更が即座に反映される

# 4. ターミナル2でCLIの動作も確認
(.venv) $ phoenix some-command
```

-----

## 📦 `core`パッケージのPyPI公開

この構成から特定のパッケージ（例: `phoenix-core`）だけをライブラリとして公開することも簡単です。

### 1\. `phoenix-core`の`pyproject.toml`を整備

公開に必要な著者情報やライセンスなどを追記します。

```toml
# packages/phoenix-core/pyproject.toml
[project]
name = "phoenix-core"
version = "1.0.0"
description = "Project Phoenixのコアビジネスロジック..."
readme = "README.md"
license = { text = "MIT" }
authors = [{ name = "Your Name", email = "your@email.com" }]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]
# ...
```

### 2\. ビルドとアップロード

**公開したいパッケージのディレクトリに移動して**、ビルドとアップロードを実行します。

```bash
# まず、coreパッケージのディレクトリへ移動
$ cd packages/phoenix-core

# 必要なツールをインストール
(.venv) $ pip install build twine

# ビルド実行（dist/フォルダが作られる）
(.venv) $ python -m build

# PyPIへアップロード
(.venv) $ twine upload dist/*
```

-----

## 🌐 開発環境と本番環境の使い分け

公開したパッケージを他の製品（`api`など）でどう使うかは、環境によって切り替えるのがベストプラクティスです。

  * **開発中 (`Development`)**

      * 常にローカルの最新ソースコードを参照し、迅速な開発サイクルを実現します。

    **`packages/phoenix-api/pyproject.toml` (開発時)**

    ```toml
    [project]
    dependencies = [
        "phoenix-core @ file:../phoenix-core", # 👈 ローカルファイルを参照
        # ...
    ]
    ```

  * **本番デプロイ時 (`Production`)**

      * PyPIから、テスト済みの安定したバージョンをインストールし、信頼性を確保します。

    **`packages/phoenix-api/pyproject.toml` (本番用)**

    ```toml
    [project]
    dependencies = [
        "phoenix-core == 1.0.0", # 👈 PyPIからバージョンを指定して参照
        # ...
    ]
    ```

-----

## ✨ まとめ：この戦略がもたらす価値

  * **モジュール性**: `core`は完全に独立しており、将来のどんな製品からも再利用できる資産となる。
  * **関心の分離**: 「ビジネスロジックは`core`」「APIのエンドポイントは`api`」と役割が明確で、コードが迷子にならない。
  * **開発のしやすさ**: すべての変更を一つのプルリクエストで管理でき、安全かつ効率的な開発が実現する。
  * **明確な依存関係**: `pyproject.toml`と単一のロックファイルにより、プロジェクト全体の依存関係が常に明確になる。
  * **高い拡張性**: 新しい「おかず」（パッケージ）を追加するだけで、既存の構造を壊すことなくシステムを成長させられる。

この設計ガイドをチームの共通言語とし、一貫性のある高品質なソフトウェア開発を目指しましょう。