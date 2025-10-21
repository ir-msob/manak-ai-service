import logging
import os
import re
from pathlib import Path
from typing import Optional, Any, Dict, Iterable

import yaml
from pydantic import ValidationError

from src.main.python.ir.msob.manak.ai.config.config_models import RootProperties

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Loads YAML into RootProperties, resolves ${models.*} placeholders,
    and applies environment overrides. The env-prefix is a class-level
    constant: set ConfigLoader.ENV_PREFIX = "MYAPP_" (or "" for no prefix).
    """

    ENV_PREFIX: str = ""

    PLACEHOLDER_RE = re.compile(r"\$\{models\.([^}]+)\}")

    def __init__(self, path: Optional[str] = None):
        self.env_prefix = self.ENV_PREFIX.upper() if self.ENV_PREFIX else None

        # -----------------------------
        # 1️⃣ Determine YAML file path
        # -----------------------------
        env_path = os.getenv("CONFIG_PATH")
        if env_path:
            path = env_path
            logger.info(f"Using CONFIG_PATH from environment: {path}")

        if path is None:
            path = self._find_default_config_path()

        logger.info(f"Loading configuration file: {path}")

        if not Path(path).exists():
            raise FileNotFoundError(f"Configuration file not found at: {path}")

        # -----------------------------
        # 2️⃣ Read YAML file
        # -----------------------------
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_text = f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read config file at {path}: {e}")

        # -----------------------------
        # 3️⃣ Extract models and replace placeholders
        # -----------------------------
        try:
            parsed = yaml.safe_load(raw_text) or {}
        except yaml.YAMLError as e:
            raise RuntimeError(f"Failed to parse YAML config: {e}")

        models_dict = parsed.get("models", {}) or {}

        def _replace(match: re.Match) -> str:
            key = match.group(1)
            if key not in models_dict or models_dict[key] is None:
                raise KeyError(f"Placeholder ${'{models.' + key + '}'} not found in models section.")
            return str(models_dict[key])

        replaced_text = self.PLACEHOLDER_RE.sub(_replace, raw_text)

        # -----------------------------
        # 4️⃣ Final load
        # -----------------------------
        try:
            final_raw: Dict[str, Any] = yaml.safe_load(replaced_text) or {}
        except yaml.YAMLError as e:
            raise RuntimeError(f"Failed to parse YAML after placeholder replacement: {e}")

        # -----------------------------
        # 5️⃣ Apply environment overrides (env wins by default)
        # -----------------------------
        try:
            self._apply_env_overrides(final_raw)
        except Exception as e:
            raise RuntimeError(f"Failed while applying environment overrides: {e}")

        # -----------------------------
        # 6️⃣ Validate with pydantic model
        # -----------------------------
        try:
            self.config: RootProperties = RootProperties(**final_raw)
        except ValidationError as e:
            raise RuntimeError(f"Invalid configuration structure: {e}")

        logger.info("Configuration successfully loaded, environment overrides applied, and validated.")

    @staticmethod
    def _set_in_dict_robust(d: Dict[str, Any], keys: Iterable[str], value: Any) -> None:
        cur = d
        keys = list(keys)
        for i, k in enumerate(keys):
            if i == len(keys) - 1:
                cur[k] = value
            else:
                if k not in cur or not isinstance(cur[k], dict):
                    cur[k] = {}
                cur = cur[k]

    def _apply_env_overrides(self, data: Dict[str, Any]) -> None:
        """
        Iterate environment variables and apply overrides to `data`.
        - If ENV_PREFIX (class const) is non-empty, only env vars starting with that prefix are considered.
        - Env var name => keys: split by '_' and lowercase, e.g. SERVER_PORT -> ['server','port'].
        - Value is parsed with yaml.safe_load to try to coerce to proper type (int/bool/...).
        """
        env_items = os.environ.items()
        for raw_k, raw_v in env_items:
            key = raw_k.upper()
            # filter by prefix if configured
            if self.env_prefix:
                if not key.startswith(self.env_prefix):
                    continue
                # strip prefix and any leading underscore(s)
                key = key[len(self.env_prefix):]
                if key.startswith("_"):
                    key = key.lstrip("_")

            if not key:
                continue

            parts = [p.lower() for p in key.split("_") if p != ""]
            if not parts:
                continue

            try:
                parsed_val = yaml.safe_load(raw_v)
            except Exception:
                parsed_val = raw_v

            try:
                self._set_in_dict_robust(data, parts, parsed_val)
                logger.debug(f"Applied env override: {raw_k} -> {'.'.join(parts)} = {parsed_val!r}")
            except Exception as e:
                logger.warning(f"Could not apply env var {raw_k} to config path {parts}: {e}")

    # -----------------------------
    # 🔍 Default path finder (unchanged)
    # -----------------------------
    def _find_default_config_path(self) -> str:
        current = Path(__file__).resolve()
        tried = []

        candidates_suffixes = [
            Path("resources/config/config.yaml"),
            Path("main/resources/config/config.yaml"),
            Path("src/main/resources/config/config.yaml"),
            Path("src/main/python/../resources/config/config.yaml"),
        ]

        while True:
            parent = current if current.is_dir() else current.parent
            if parent == parent.parent:
                break

            for suffix in candidates_suffixes:
                candidate = (parent / suffix).resolve()
                tried.append(str(candidate))
                if candidate.exists():
                    logger.info(f"Found config file at: {candidate}")
                    return str(candidate)

            if (parent / ".git").exists() or (parent / "pyproject.toml").exists() or (parent / "setup.py").exists():
                extra = (parent / "src/main/resources/config/config.yaml").resolve()
                tried.append(str(extra))
                if extra.exists():
                    logger.info(f"Found config file at: {extra}")
                    return str(extra)
                break

            current = parent

        logger.error("Tried the following candidate paths for config but none existed:\n" + "\n".join(tried))
        raise FileNotFoundError(
            "Cannot locate 'src/main/resources/config/config.yaml' or common alternatives. "
            "Set CONFIG_PATH env var to specify custom location."
        )

    def get_config(self) -> RootProperties:
        """Returns the loaded configuration object."""
        return self.config
