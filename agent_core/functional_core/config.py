import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


CONFIG_PATH = Path("config.yaml")
DEFAULT_LOG_DIR = Path("logs")


@dataclass
class LLMConfig:
    mode: str = "local"
    base_url: str = "http://127.0.0.1:1234/v1/chat/completions"
    timeout: int = 20
    model: Optional[str] = None


@dataclass
class DiscordConfig:
    token: Optional[str] = None
    channel_id: Optional[int] = None


@dataclass
class OBSConfig:
    host: str = "127.0.0.1"
    port: int = 4455
    password: Optional[str] = None


@dataclass
class OverlayConfig:
    host: str = "0.0.0.0"
    port: int = 8765


@dataclass
class AppConfig:
    llm: LLMConfig
    discord: DiscordConfig
    obs: OBSConfig
    overlay: OverlayConfig
    log_level: str = "INFO"


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _env_override(value: Any, env_key: str, cast_type):
    env_val = os.getenv(env_key)
    if env_val is None:
        return value
    try:
        return cast_type(env_val)
    except (TypeError, ValueError):
        logging.warning("Invalid value for %s; using default.", env_key)
        return value


def _build_llm_config(data: Dict[str, Any]) -> LLMConfig:
    llm_data = data.get("llm", {})
    return LLMConfig(
        mode=_env_override(llm_data.get("mode", "local"), "LLM_MODE", str),
        base_url=_env_override(
            llm_data.get("base_url", "http://127.0.0.1:1234/v1/chat/completions"),
            "LLM_BASE_URL",
            str,
        ),
        timeout=_env_override(llm_data.get("timeout", 20), "LLM_TIMEOUT", int),
        model=_env_override(llm_data.get("model"), "LLM_MODEL", str),
    )


def _build_discord_config(data: Dict[str, Any]) -> DiscordConfig:
    discord_data = data.get("discord", {})
    token = os.getenv("DISCORD_BOT_TOKEN", discord_data.get("token"))
    channel = discord_data.get("channel_id")
    channel_env = os.getenv("DISCORD_CHANNEL_ID")
    if channel_env:
        try:
            channel = int(channel_env)
        except ValueError:
            logging.warning("DISCORD_CHANNEL_ID must be an integer.")
    return DiscordConfig(token=token, channel_id=channel)


def _build_obs_config(data: Dict[str, Any]) -> OBSConfig:
    obs_data = data.get("obs", {})
    return OBSConfig(
        host=_env_override(obs_data.get("host", "127.0.0.1"), "OBS_HOST", str),
        port=_env_override(obs_data.get("port", 4455), "OBS_PORT", int),
        password=os.getenv("OBS_PASSWORD", obs_data.get("password")),
    )


def _build_overlay_config(data: Dict[str, Any]) -> OverlayConfig:
    overlay_data = data.get("overlay", {})
    return OverlayConfig(
        host=_env_override(overlay_data.get("host", "0.0.0.0"), "OVERLAY_HOST", str),
        port=_env_override(overlay_data.get("port", 8765), "OVERLAY_PORT", int),
    )


def load_config(path: Optional[Path] = None) -> AppConfig:
    cfg_path = path or CONFIG_PATH
    raw_data = _load_yaml(cfg_path)

    llm_cfg = _build_llm_config(raw_data)
    discord_cfg = _build_discord_config(raw_data)
    obs_cfg = _build_obs_config(raw_data)
    overlay_cfg = _build_overlay_config(raw_data)
    log_level = raw_data.get("log_level", os.getenv("LOG_LEVEL", "INFO"))

    DEFAULT_LOG_DIR.mkdir(exist_ok=True)

    return AppConfig(
        llm=llm_cfg,
        discord=discord_cfg,
        obs=obs_cfg,
        overlay=overlay_cfg,
        log_level=log_level,
    )


__all__ = [
    "AppConfig",
    "DiscordConfig",
    "LLMConfig",
    "OBSConfig",
    "OverlayConfig",
    "load_config",
]
