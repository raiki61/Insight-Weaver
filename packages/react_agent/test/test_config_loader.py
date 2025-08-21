from pathlib import Path

import pytest
from pydantic import ValidationError

from config.config_loader import load_config


def test_load_config_success(tmp_path: Path, monkeypatch):
    """正常系: 設定ファイルと環境変数が正しく読み込めることをテスト"""

    monkeypatch.setenv("API_KEY", "my-secret-key-from-env")

    # ダミーの config.yml をPydanticモデルの構造に合わせて修正
    config_content = """
    ollama:
      base_url: "http://localhost:11434"
      model_name: "llama3"                
      temperature: 0.7                   
    """
    config_file = tmp_path / "config.yml"
    config_file.write_text(
        config_content, encoding="utf-8"
    )  # utf-8エンコーディングを明記

    # テスト対象の関数を実行
    settings = load_config(str(config_file))

    # 結果を検証
    assert settings.ollama.model_name == "llama3"
    assert settings.ollama.base_url == "http://localhost:11434"
    assert settings.ollama.temperature == 0.7


def test_load_config_missing_env_var(tmp_path: Path, monkeypatch):
    """異常系: 環境変数が設定されていない場合にValueErrorが発生することをテスト"""
    # 必要な環境変数がセットされていない状態を作る
    monkeypatch.delenv("API_KEY", raising=False)

    # ダミーの config.yml を作成
    config_content = "ollama:\n  api_key: ${API_KEY}\n  model: 'llama3'"
    config_file = tmp_path / "config.yml"
    config_file.write_text(config_content)

    # pytest.raisesを使って、特定の例外が発生することを検証する
    with pytest.raises(ValueError, match="環境変数 'API_KEY' が設定されていません。"):
        load_config(str(config_file))


def test_load_config_validation_error(tmp_path: Path):
    """異常系: 設定の構造が不正な場合にpydanticのValidationErrorが発生することをテスト"""
    # Pydanticモデルの必須項目 `model` が欠けているYAMLを作成
    config_content = "ollama:\n  api_key: 'dummy-key'"
    config_file = tmp_path / "config.yml"
    config_file.write_text(config_content)

    with pytest.raises(ValidationError):
        load_config(str(config_file))
