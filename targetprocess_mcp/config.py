"""Configuration management for TargetProcess MCP."""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

KEYCHAIN_SERVICE = "targetprocess-mcp"
CONFIG_DIR = Path.home() / ".config" / "targetprocess-mcp"

_vpn_check_cache: tuple[bool, float] | None = None
_VPN_CHECK_TTL = 30.0

_config_cache: dict[str, Any] | None = None
_token_cache: str | None = None


def get_token() -> str | None:
    """Retrieve token from macOS Keychain."""
    global _token_cache
    if _token_cache is not None:
        return _token_cache

    try:
        result = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-s",
                KEYCHAIN_SERVICE,
                "-a",
                "api-token",
                "-w",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            _token_cache = result.stdout.strip()
            return _token_cache
    except Exception:
        pass
    return None


def load_config() -> dict[str, Any]:
    """Load configuration from file."""
    global _config_cache
    if _config_cache is not None:
        return _config_cache

    config_file = CONFIG_DIR / "config.toml"
    if config_file.exists():
        try:
            with open(config_file, "rb") as f:
                _config_cache = tomllib.load(f)
                return _config_cache
        except Exception:
            pass
    _config_cache = {}
    return _config_cache


def reload_config() -> dict[str, Any]:
    """Force reload configuration from file."""
    global _config_cache, _token_cache
    _config_cache = None
    _token_cache = None
    return load_config()


class _Config:
    """Lazy-loaded configuration accessor."""

    @property
    def targetprocess_url(self) -> str:
        url = os.getenv("TARGETPROCESS_URL")
        if url:
            return url
        return load_config().get("URL", "")

    @property
    def targetprocess_token(self) -> str:
        token = os.getenv("TARGETPROCESS_TOKEN")
        if token:
            return token
        return get_token() or ""

    @property
    def vpn_required(self) -> bool:
        if os.getenv("TARGETPROCESS_VPN_REQUIRED", "").lower() == "true":
            return True
        return load_config().get("VPN_REQUIRED", False)

    @property
    def vpn_check_hosts(self) -> list[str]:
        return load_config().get("VPN_CHECK_HOSTS", [])

    @property
    def api_base(self) -> str:
        url = self.targetprocess_url
        token = self.targetprocess_token
        if url and token:
            return f"{url.rstrip('/')}/api/v1"
        return ""


config = _Config()


def check_vpn() -> bool:
    """Check if VPN is connected (if required by configuration)."""
    global _vpn_check_cache

    if not config.vpn_required:
        return True

    if not config.vpn_check_hosts:
        return True

    now = time.monotonic()
    if _vpn_check_cache is not None:
        result, cached_time = _vpn_check_cache
        if now - cached_time < _VPN_CHECK_TTL:
            return result

    for host in config.vpn_check_hosts:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((host, 443))
            sock.close()
            _vpn_check_cache = (True, now)
            return True
        except Exception:
            try:
                socket.gethostbyname(host)
                _vpn_check_cache = (True, now)
                return True
            except Exception:
                continue

    _vpn_check_cache = (False, now)
    return False
