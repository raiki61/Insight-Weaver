# config/config_loader.py
import os
from typing import Any, Optional

import yaml
from dotenv import load_dotenv

from .config import Config
from .env_resolver import interpolate_tree


def load_config(
    path: str,
    *,
    dotenv_path: Optional[str] = None,
    override_env: bool = False,
    strict_env: bool = True,
) -> Config:
    """
    設定ファイルを読み込み、環境変数展開し、Pydantic で検証して返す。
    - dotenv_path: .env のパス（None ならカレント等の既定探索）
    - override_env: True で .env が OS 環境を上書き、False で OS 環境が優先
    - strict_env: True で未定義 ${VAR} は例外。False なら置換せず残す。
    """
    # 1) .env 読み込み
    load_dotenv(dotenv_path, override=override_env)

    # 2) YAML 読み込み
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    # 3) 環境変数・~・$VAR 展開（共通ユーティリティ）
    processed = interpolate_tree(raw, strict=strict_env)

    # 4) Pydantic 検証
    return Config.model_validate(processed)
