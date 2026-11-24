"""Loads the configuration from the .env file at the project root."""
import os
from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

from src.enums import Browser, TracingMode

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    base_url: str
    browser: Browser
    browser_channel: str | None
    headless: bool
    slow_mo: float
    timeout_ms: float
    tracing: TracingMode
    record_video: bool


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing variable '{name}' in the .env file")
    return value


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if not value:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _choice(name: str, enum_type: type[StrEnum], default: StrEnum) -> StrEnum:
    value = (os.getenv(name) or default).strip().lower()
    try:
        return enum_type(value)
    except ValueError as exc:
        allowed = ", ".join(item.value for item in enum_type)
        raise RuntimeError(f"Invalid value '{value}' for '{name}'. Allowed: {allowed}") from exc


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        base_url=_required("BASE_URL").rstrip("/"),
        browser=_choice("BROWSER", Browser, Browser.CHROMIUM),
        browser_channel=os.getenv("BROWSER_CHANNEL") or None,
        headless=_bool("HEADLESS", True),
        slow_mo=float(os.getenv("SLOW_MO") or 0),
        timeout_ms=float(os.getenv("TIMEOUT") or 45) * 1000,
        tracing=_choice("TRACING", TracingMode, TracingMode.ALWAYS),
        record_video=_bool("RECORD_VIDEO", False),
    )
