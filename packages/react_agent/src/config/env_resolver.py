# config/env_resolver.py
from __future__ import annotations

import os
import re
import sys
from typing import Any, Dict, Mapping, Optional

# ${VAR} または ${VAR:-default} に対応する正規表現
_PATTERN = re.compile(
    r"\$\{(?P<var>[A-Za-z_][A-Za-z0-9_]*)(?::-(?P<default>.*?))?\}"
)


def merge_safe_stdio_env(
    user_env: Optional[Dict[str, str]],
) -> Optional[Dict[str, str]]:
    """
    stdio 起動時の env マージ:
    - PATH 等の安全な既定環境を引き継いだ上で user_env を上書き
    - user_env が None/空なら None を返す（明示指定なし）
    """
    if not user_env:
        return None

    if sys.platform == "win32":
        keys = [
            "APPDATA",
            "HOMEDRIVE",
            "HOMEPATH",
            "LOCALAPPDATA",
            "PATH",
            "PROCESSOR_ARCHITECTURE",
            "SYSTEMDRIVE",
            "SYSTEMROOT",
            "TEMP",
            "USERNAME",
            "USERPROFILE",
        ]
    else:
        keys = ["HOME", "LOGNAME", "PATH", "SHELL", "TERM", "USER"]

    base: Dict[str, str] = {}
    for k in keys:
        v = os.environ.get(k)
        if v and not v.startswith("()"):  # 関数定義は除外
            base[k] = v

    base.update(user_env)
    return base


def interpolate_string(
    s: str,
    env: Optional[Mapping[str, str]] = None,
    *,
    strict: bool = True,
    expand_user: bool = True,
    expand_plain_dollar: bool = True,
) -> str:
    """
    文字列中の ${VAR} / ${VAR:-default} を展開し、必要なら ~ と $VAR も展開する。
    strict=True のとき未定義VARは例外。False のときは置換せず残す。
    """
    env = dict(os.environ if env is None else env)

    # 先に ~ を展開
    if expand_user:
        s = os.path.expanduser(s)

    # ${VAR} と ${VAR:-default}
    def _repl(m: re.Match) -> str:
        var = m.group("var")
        default = m.group("default")

        if var in env and env[var] != "":
            return env[var]
        if default is not None:
            return default or ""
        if strict:
            raise ValueError(f"環境変数 '{var}' が設定されていません。")
        return m.group(0)

    s = _PATTERN.sub(_repl, s)

    # $VAR 形式の展開（必要な場合のみ）
    if expand_plain_dollar:
        s = os.path.expandvars(s)

    return s


def interpolate_tree(
    data: Any,
    env: Optional[Mapping[str, str]] = None,
    *,
    strict: bool = True,
    expand_user: bool = True,
    expand_plain_dollar: bool = True,
) -> Any:
    """
    dict/list/str を再帰走査して文字列を展開。
    """
    if isinstance(data, dict):
        return {
            k: interpolate_tree(
                v,
                env,
                strict=strict,
                expand_user=expand_user,
                expand_plain_dollar=expand_plain_dollar,
            )
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [
            interpolate_tree(
                x,
                env,
                strict=strict,
                expand_user=expand_user,
                expand_plain_dollar=expand_plain_dollar,
            )
            for x in data
        ]
    if isinstance(data, str):
        return interpolate_string(
            data,
            env,
            strict=strict,
            expand_user=expand_user,
            expand_plain_dollar=expand_plain_dollar,
        )
    return data
