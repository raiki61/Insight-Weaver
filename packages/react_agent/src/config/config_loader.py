import os
from typing import Any

import yaml
from dotenv import load_dotenv

from .config import Config


def _replace_env_vars(config: Any) -> Any:
    """設定データ内のプレースホルダー `${VAR}` を環境変数の値で再帰的に置換する"""
    if isinstance(config, dict):
        return {k: _replace_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_replace_env_vars(i) for i in config]
    elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
        env_var = config[2:-1]  # `${VAR}` から `VAR` を抽出
        value = os.environ.get(env_var)
        if value is None:
            raise ValueError(f"環境変数 '{env_var}' が設定されていません。")
        return value
    return config


def load_config(path: str) -> Config:
    """
    設定ファイルを読み込み、環境変数で値を置換し、Pydanticモデルで検証して返す。
    """
    # 1. .env ファイルを読み込み、環境変数を設定
    load_dotenv()

    # 2. YAML ファイルを辞書として読み込む
    with open(path, 'r', encoding='utf-8') as f:
        raw_config = yaml.safe_load(f)

    # 3. 環境変数でプレースホルダーを置換
    processed_config = _replace_env_vars(raw_config)

    # 4. Pydanticモデルにデータを流し込み、バリデーションを実行
    try:
        config = Config(**processed_config)
        return config
    except Exception as e:
        print(f"設定のバリデーションに失敗しました: {e}")
        raise