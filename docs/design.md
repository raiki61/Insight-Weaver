承知いたしました。
これまでの対話を基に、ご提案のプロジェクト「AI議事録分析アシスタント」の基本設計書を作成します。この設計書は、プロジェクトの全体像、機能、技術的な仕様を明確にし、開発チームや関係者間の共通認識を形成するためのものです。

-----

## 基本設計書：AI議事録分析アシスタント

**文書バージョン:** 1.0
**作成日:** 2025年6月20日
**作成者:** Gemini

### 1\. 概要

#### 1.1. プロジェクト名

AI議事録分析アシスタント（コードネーム: Insight Weaver）

#### 1.2. 目的と背景

音声認識によってテキスト化された会議やインタビューの議事録（トランスクリプト）は、そのままだと情報量が多すぎて活用しづらい。本プロジェクトは、LLM（大規模言語モデル）を活用して、この長大なテキストデータから価値ある「知的資産」を自動抽出し、情報整理の時間を劇的に削減することを目的とする。

#### 1.3. 解決する課題

  * 会議後の議事録作成・要約にかかる多大な時間と労力
  * 議事録に埋もれてしまう決定事項やタスク（アクションアイテム）の見落とし
  * 発言内容の事実確認（ファクトチェック）の手間
  * 過去の議論内容の検索・再利用の困難さ

#### 1.4. ターゲットユーザー

  * プロジェクトマネージャー、チームリーダー
  * 営業担当者、コンサルタント
  * 議事録作成を担当するすべてのビジネスパーソン

### 2\. 機能要件

#### 2.1. コア機能

  * **入力:** 音声ファイル（.mp3, .wav等）、テキストファイル（.txt, .md）、Teamsトランスクリプトのペーストに対応。
  * **要約:** 議事録全体の要約、または指定箇所の要約を生成する。
  * **アクションアイテム抽出:** テキストから「誰が」「何を」「いつまでに行うか」というタスクを抽出し、リスト化する。
  * **ファクトチェック:** テキスト内の固有名詞や数値情報などを、Web検索を通じて事実確認する。
  * **関連情報付与:** テキスト内のキーワードに関連する社内ドキュメントやWeb上の参考リンクを提示する。
  * **辛口フィードバック:** 提案内容などに対して、AIが批判的な視点からリスクや改善点を指摘する。
  * **対話による深掘り:** チャット形式で、生成された結果に対して追加の質問や分析指示を行える。
  * **結果のエクスポート:** 生成された要約やアクションアイテムリストをMarkdownやCSV形式でダウンロードできる。

### 3\. UI/UX設計

#### 3.1. UIコンセプト

**対話型分析ダッシュボード**
「原文（一次情報）」「対話（思考プロセス）」「成果物（知的資産）」を一つの画面に統合し、ユーザーの思考を妨げないシームレスな分析体験を提供する。

#### 3.2. 画面構成

以下の3パネル構成とする。

| パネル | 名称 | 役割 | 主要機能 |
| :--- | :--- | :--- | :--- |
| **左** | **原文パネル** | オリジナルの議事録テキストを表示 | ・インタラクティブ・ハイライト\<br\>・テキスト選択からのアクション実行 |
| **中央** | **対話パネル** | AIとの対話を行う | ・スラッシュコマンドによる機能実行\<br\>・スレッド形式での対話 |
| **右** | **インサイト・パネル** | 生成された知的資産を整理・蓄積 | ・タブ切り替え（要約、タスク等）\<br\>・インタラクティブなウィジェット（チェックボックス等）\<br\>・エクスポート機能 |

### 4\. システム構成と使用技術

#### 4.1. システムアーキテクチャ

#### 4.2. 技術スタック

| 領域 | 使用技術 | 選択理由 |
| :--- | :--- | :--- |
| **フロントエンド** | **Next.js (React), Vercel AI SDK, shadcn/ui** | モダンで高速なUIと、リアルタイムなストリーミング表示を効率的に実装するため。 |
| **バックエンド** | **Python, FastAPI** | 非同期処理による高いパフォーマンスと、WebSocket/ストリーミング応答を容易に実装できるため。 |
| **LLM連携** | **LangChain** | LLMとの複雑な処理フロー（RAG、会話履歴管理など）を柔軟かつ堅牢に構築するため。 |
| **音声認識** | **Hugging Face Transformers (Whisper)** | 日英に特化したモデルの利用や、将来的な自前でのファインチューニングを見据えた拡張性のため。 |
| **データベース** | **PostgreSQL, ChromaDB (or Pinecone)** | 構造化データ（ユーザー情報等）と、RAG用のベクトルデータを効率的に管理するため。 |
| **LLMモデル** | **GPT-4o / Gemini 1.5 Pro (API経由)** | 高度な日本語能力と指示追従性を持つ最新モデルを利用するため。プロジェクトの性質に応じて選択。 |
| **インフラ** | **Docker, AWS/GCP/Vercel (検討)** | コンテナ技術によるポータビリティの確保と、スケーラブルなクラウド環境へのデプロイを想定。 |

### 5\. データモデル（簡易版）

  * **Users:** ユーザー情報を管理
  * **Documents:** アップロードされた原文テキストとメタデータ（ファイル名、作成日）を管理
  * **ChatSessions:** 各ドキュメントに対する一連の対話を管理
  * **Insights:** 生成された知的資産（要約、ファクトチェック結果等）を種類別に管理
  * **ActionItems:** 抽出されたタスクを管理（内容、担当者、期限、完了ステータス）
  * **VectorChunks:** RAGのために原文を分割し、ベクトル化したデータをメタデータと共に格納

### 6\. 開発ステップ（マイルストーン案）

#### フェーズ1：MVP (Minimum Viable Product) 開発 (1〜2ヶ月)

  * 3パネルUIの基本骨格を実装。
  * テキスト入力、要約、アクションアイテム抽出のコア機能を実装。
  * ユーザー認証とドキュメント保存機能。

#### フェーズ2：機能拡張とRAGの実装 (3〜4ヶ月)

  * **インタラクティブ・ハイライト機能**の実装。
  * ファクトチェック、関連情報付与機能（RAGアーキテクチャの構築）。
  * 結果のエクスポート機能。

#### フェーズ3：高度化と運用改善 (5ヶ月目〜)

  * 音声ファイル入力とWhisperモデルの連携。
  * 外部タスク管理ツール（Asana, Jira等）とのAPI連携。
  * ユーザーフィードバックに基づくUI/UXの改善とパフォーマンスチューニング。


### backend architecture

```mermaid
graph LR
    %% --- Component Definitions ---

    actor User;

    subgraph "User Side"
        Client["Frontend <br> Next.js / Vercel AI SDK"];
    end

    subgraph "Our Service Backend (Cloud)"
        subgraph "API Server (FastAPI)"
            id_api["API Gateway / Endpoints"];
            id_orchestrator["<b>LangChain Orchestrator</b>"];
            id_rag["RAG Components <br> Retriever, Chunker, Embedding"];
        end

        subgraph "Data Stores"
            id_db[("PostgreSQL <br> Users, Documents, Sessions")];
            id_vectordb[("Vector DB <br> ChromaDB / Pinecone")];
        end
    end

    subgraph "External Services"
        id_llm_api["LLM API <br> OpenAI / Google"];
        id_search_api["Web Search API <br> Google / Bing"];
    end

    %% --- Flow Definitions ---

    %% User Interaction
    User -- "1. Interact" --> Client;
    Client <-.->|"2. Real-time UI<br>(WebSocket / SSE)"| id_api;
    Client -- "3. API Requests<br>(HTTPS)"--> id_api;

    %% Backend Internal Logic
    id_api --> id_orchestrator;
    id_orchestrator -- "Writes/Reads Metadata" --> id_db;

    %% MVP Flow (Dashed Line)
    id_orchestrator -.->|"<b>[MVP Flow]</b><br>Prompt only"| id_llm_api;

    %% RAG Flow (Solid Line)
    id_orchestrator -- "<b>[RAG Flow]</b><br>Query" --> id_rag;
    id_rag -- "Retrieves context" --> id_vectordb;
    id_rag -- "Searches web" --> id_search_api;
    id_rag -- "Prompt with Context" --> id_llm_api;

    %% Document Upload Flow
    id_api -- "Uploaded Doc" --> id_rag;
    id_rag -- "Saves vectors" --> id_vectordb;
```