from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from kidschef_backend.config import OllamaConfig, load_env_file


class ConfigEnvTests(unittest.TestCase):
    def test_load_env_file_populates_missing_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            env_path = Path(tmp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "KIDS_CHEF_OLLAMA_ENABLED=true",
                        "KIDS_CHEF_OLLAMA_HOST=http://127.0.0.1:11434",
                        "KIDS_CHEF_OLLAMA_MODEL=llama3.2:latest",
                    ]
                ),
                encoding="utf-8",
            )

            original = {key: os.environ.get(key) for key in (
                "KIDS_CHEF_OLLAMA_ENABLED",
                "KIDS_CHEF_OLLAMA_HOST",
                "KIDS_CHEF_OLLAMA_MODEL",
            )}
            try:
                for key in original:
                    os.environ.pop(key, None)
                loaded = load_env_file(env_path)
                config = OllamaConfig.from_env()
            finally:
                for key, value in original.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

        self.assertTrue(loaded)
        self.assertTrue(config.is_enabled)
        self.assertEqual(config.host, "http://127.0.0.1:11434")
        self.assertEqual(config.model, "llama3.2:latest")

    def test_load_env_file_does_not_override_existing_process_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            env_path = Path(tmp_dir) / ".env"
            env_path.write_text("KIDS_CHEF_OLLAMA_MODEL=llama3.2:latest\n", encoding="utf-8")

            original = os.environ.get("KIDS_CHEF_OLLAMA_MODEL")
            os.environ["KIDS_CHEF_OLLAMA_MODEL"] = "gpt-oss:latest"
            try:
                load_env_file(env_path)
                config = OllamaConfig.from_env()
            finally:
                if original is None:
                    os.environ.pop("KIDS_CHEF_OLLAMA_MODEL", None)
                else:
                    os.environ["KIDS_CHEF_OLLAMA_MODEL"] = original

        self.assertEqual(config.model, "gpt-oss:latest")


if __name__ == "__main__":
    unittest.main()
