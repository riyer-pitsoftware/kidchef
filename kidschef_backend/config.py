"""Environment-driven configuration for the local backend."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _as_float(value: str | None, default: float) -> float:
    if value is None:
        return default
    try:
        return max(0.1, float(value))
    except ValueError:
        return default


def _as_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def load_env_file(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False

    loaded = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if value and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ.setdefault(key, value)
        loaded = True
    return loaded


@dataclass(frozen=True, slots=True)
class OllamaConfig:
    enabled: bool = False
    host: str = "http://127.0.0.1:11434"
    model: str = "llama3.2"
    timeout_seconds: float = 5.0
    max_candidates: int = 5

    @classmethod
    def from_env(cls) -> "OllamaConfig":
        return cls(
            enabled=_as_bool(os.getenv("KIDS_CHEF_OLLAMA_ENABLED"), default=False),
            host=os.getenv("KIDS_CHEF_OLLAMA_HOST", "http://127.0.0.1:11434").strip() or "http://127.0.0.1:11434",
            model=os.getenv("KIDS_CHEF_OLLAMA_MODEL", "llama3.2").strip() or "llama3.2",
            timeout_seconds=_as_float(os.getenv("KIDS_CHEF_OLLAMA_TIMEOUT_SECONDS"), 5.0),
            max_candidates=max(1, min(_as_int(os.getenv("KIDS_CHEF_OLLAMA_MAX_CANDIDATES"), 5), 20)),
        )

    @property
    def is_enabled(self) -> bool:
        return self.enabled and bool(self.host.strip()) and bool(self.model.strip())
