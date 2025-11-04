import logging
import os
import re
import time
from pathlib import Path
from typing import Optional, Any, Dict, Iterable

import yaml
from pydantic import ValidationError

from src.main.python.ir.msob.manak.ai.config.config_models import RootProperties

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Loads YAML into RootProperties, resolves ${...} placeholders
    (not only models.*) and applies environment overrides.
    This version resolves dotted paths like ${python.application.name}
    and ${server.port} by looking them up in the YAML structure.
    """

    ENV_PREFIX: str = ""
    # general placeholder matcher: ${some.path.here}
    PLACEHOLDER_RE = re.compile(r"\$\{([^}]+)\}")

    def __init__(self, path: Optional[str] = None):
        start_total = time.perf_counter()
        logger.debug("ConfigLoader: __init__ start (CONFIG_PATH=%s)", os.getenv("CONFIG_PATH"))

        try:
            t0 = time.perf_counter()
            self.env_prefix = self.ENV_PREFIX.upper() if self.ENV_PREFIX else None

            # -----------------------------
            # 1️⃣ Determine YAML file path
            # -----------------------------
            env_path = os.getenv("CONFIG_PATH")
            if env_path:
                path = env_path
                logger.info("ConfigLoader: Using CONFIG_PATH from environment: %s", path)

            if path is None:
                logger.debug("ConfigLoader: no explicit path provided, locating default...")
                path = self._find_default_config_path()

            logger.info("ConfigLoader: resolved config path -> %s", path)
            logger.debug("ConfigLoader: path resolution took %.3f sec", time.perf_counter() - t0)

            # existence check
            if not Path(path).exists():
                raise FileNotFoundError(f"Configuration file not found at: {path}")

            # -----------------------------
            # 2️⃣ Read YAML file
            # -----------------------------
            t1 = time.perf_counter()
            try:
                with open(path, "r", encoding="utf-8") as f:
                    raw_text = f.read()
                logger.debug("ConfigLoader: read raw_text (length=%d)", len(raw_text))
            except Exception as e:
                logger.exception("ConfigLoader: failed to read config file at %s", path)
                raise RuntimeError(f"Failed to read config file at {path}: {e}") from e
            logger.debug("ConfigLoader: file read took %.3f sec", time.perf_counter() - t1)

            # -----------------------------
            # 3️⃣ Resolve placeholders iteratively
            # -----------------------------
            t2 = time.perf_counter()
            try:
                replaced_text = self._resolve_placeholders_iterative(raw_text)
                logger.debug("ConfigLoader: placeholder replacement done (replaced_text length=%d)", len(replaced_text))
            except Exception as e:
                logger.exception("ConfigLoader: failed during placeholder replacement")
                raise
            logger.debug("ConfigLoader: placeholder replacement took %.3f sec", time.perf_counter() - t2)

            # -----------------------------
            # 4️⃣ Final load
            # -----------------------------
            t3 = time.perf_counter()
            try:
                final_raw: Dict[str, Any] = yaml.safe_load(replaced_text) or {}
                logger.debug("ConfigLoader: final_raw top keys: %s", list(final_raw.keys()))
            except yaml.YAMLError as e:
                logger.exception("ConfigLoader: YAML parse error after replacement")
                raise RuntimeError(f"Failed to parse YAML after placeholder replacement: {e}") from e
            logger.debug("ConfigLoader: final YAML load took %.3f sec", time.perf_counter() - t3)

            # -----------------------------
            # 5️⃣ Apply environment overrides (env wins by default)
            # -----------------------------
            t4 = time.perf_counter()
            try:
                overrides_applied = self._apply_env_overrides(final_raw)
                logger.debug("ConfigLoader: applied %d env overrides", overrides_applied)
            except Exception as e:
                logger.exception("ConfigLoader: failed while applying environment overrides")
                raise RuntimeError(f"Failed while applying environment overrides: {e}") from e
            logger.debug("ConfigLoader: env overrides took %.3f sec", time.perf_counter() - t4)

            # -----------------------------
            # 6️⃣ Validate with pydantic model
            # -----------------------------
            t5 = time.perf_counter()
            try:
                self.config: RootProperties = RootProperties(**final_raw)
            except ValidationError as e:
                logger.exception("ConfigLoader: pydantic validation error")
                try:
                    logger.debug("ConfigLoader: validation errors: %s", e.errors())
                except Exception:
                    pass
                raise RuntimeError(f"Invalid configuration structure: {e}") from e
            logger.debug("ConfigLoader: pydantic validation took %.3f sec", time.perf_counter() - t5)

            logger.info(
                "ConfigLoader: Configuration successfully loaded and validated (total %.3f sec).",
                time.perf_counter() - start_total,
            )

        except Exception:
            logger.exception("ConfigLoader: initialization FAILED")
            raise

    # -----------------------------
    # Helper: robustly create nested dict keys
    # -----------------------------
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

    # -----------------------------
    # Apply env overrides
    # -----------------------------
    def _apply_env_overrides(self, data: Dict[str, Any]) -> int:
        env_items = os.environ.items()
        applied = 0
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
                applied += 1
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("Applied env override: %s -> %s = %r", raw_k, ".".join(parts), parsed_val)
            except Exception as e:
                logger.warning("Could not apply env var %s to config path %s: %s", raw_k, parts, e)
        return applied

    # -----------------------------
    # Lookup dotted path in dict (e.g. "python.application.name")
    # -----------------------------
    @staticmethod
    def _lookup_path(data: Dict[str, Any], dotted_path: str) -> Any:
        parts = dotted_path.split(".")
        cur: Any = data
        for p in parts:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                raise KeyError(f"Path '{dotted_path}' not found in configuration.")
        return cur

    # -----------------------------
    # Iterative resolver for ${...} placeholders
    # -----------------------------
    def _resolve_placeholders_iterative(self, raw_text: str, max_iters: int = 10) -> str:
        """
        Repeatedly parse YAML and replace ${a.b.c} by looking up a.b.c in the
        currently-parsed tree. Iterate because replacements may expose new placeholders.
        Raises KeyError if a placeholder cannot be resolved.
        """
        text = raw_text
        for iter_no in range(max_iters):
            if not self.PLACEHOLDER_RE.search(text):
                # no placeholders left
                logger.debug("No placeholders found on iteration %d", iter_no)
                break

            parsed = yaml.safe_load(text) or {}
            # replacement function uses parsed snapshot
            def _repl(m: re.Match) -> str:
                key = m.group(1).strip()
                try:
                    val = self._lookup_path(parsed, key)
                    # convert non-str to str for insertion
                    return str(val)
                except KeyError:
                    logger.error("Placeholder %s not found in config during replacement (iteration %d)", m.group(0), iter_no)
                    # keep original behavior: fail fast so misconfigurations are visible
                    raise KeyError(f"Placeholder ${{{key}}} not found in configuration.")

            try:
                new_text = self.PLACEHOLDER_RE.sub(_repl, text)
            except KeyError:
                # bubble up so caller logs and fails
                raise
            if new_text == text:
                # nothing changed -> stop
                logger.debug("Placeholder replacement made no change on iteration %d", iter_no)
                break
            text = new_text
            logger.debug("Placeholder replacement completed iteration %d", iter_no)

        else:
            # reached max iterations
            logger.warning("Reached max placeholder resolution iterations (%d). Some placeholders may remain.", max_iters)

        # final sanity check: if placeholders remain, raise
        if self.PLACEHOLDER_RE.search(text):
            found = self.PLACEHOLDER_RE.findall(text)
            logger.error("Unresolved placeholders after resolution: %s", found)
            raise RuntimeError(f"Unresolved placeholders after {max_iters} iterations: {found}")

        return text

    # -----------------------------
    # Default path finder (unchanged)
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

        logger.debug("ConfigLoader._find_default_config_path: starting at %s", current)
        while True:
            parent = current if current.is_dir() else current.parent
            if parent == parent.parent:
                break

            for suffix in candidates_suffixes:
                candidate = (parent / suffix).resolve()
                tried.append(str(candidate))
                logger.debug("ConfigLoader._find_default_config_path: checking %s", candidate)
                if candidate.exists():
                    logger.info("ConfigLoader: Found config file at: %s", candidate)
                    return str(candidate)

            if (parent / ".git").exists() or (parent / "pyproject.toml").exists() or (parent / "setup.py").exists():
                extra = (parent / "src/main/resources/config/config.yaml").resolve()
                tried.append(str(extra))
                logger.debug("ConfigLoader._find_default_config_path: checking extra %s", extra)
                if extra.exists():
                    logger.info("ConfigLoader: Found config file at: %s", extra)
                    return str(extra)
                break

            current = parent

        logger.error("ConfigLoader: Tried the following candidate paths but none existed:\n%s", "\n".join(tried))
        raise FileNotFoundError(
            "Cannot locate 'src/main/resources/config/config.yaml' or common alternatives. "
            "Set CONFIG_PATH env var to specify custom location."
        )

    def get_properties(self) -> RootProperties:
        """Returns the loaded configuration object."""
        return self.config
