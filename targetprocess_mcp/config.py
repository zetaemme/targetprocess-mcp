"""Configuration management for TargetProcess MCP."""

import os
import subprocess
from pathlib import Path
from typing import Any

KEYCHAIN_SERVICE = "targetprocess-mcp"
CONFIG_DIR = Path.home() / ".config" / "targetprocess-mcp"


def get_token() -> str | None:
    """Retrieve token from macOS Keychain."""
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
            return result.stdout.strip()
    except Exception:
        pass
    return None


def load_config() -> dict[str, Any]:
    """Load configuration from file."""
    config_file = CONFIG_DIR / "config.py"
    if config_file.exists():
        try:
            namespace: dict[str, Any] = {}
            exec(compile(config_file.read_text(), config_file, "exec"), namespace)
            return namespace
        except Exception:
            pass
    return {}


config = load_config()

TARGETPROCESS_URL = os.getenv("TARGETPROCESS_URL", config.get("URL", ""))
TARGETPROCESS_TOKEN = os.getenv("TARGETPROCESS_TOKEN", get_token() or "")

VPN_REQUIRED = os.getenv(
    "TARGETPROCESS_VPN_REQUIRED", ""
).lower() == "true" or config.get("VPN_REQUIRED", False)
VPN_CHECK_HOSTS: list[str] = config.get("VPN_CHECK_HOSTS", [])

if not TARGETPROCESS_URL:
    raise RuntimeError(
        "TARGETPROCESS_URL not set. Run: python -m targetprocess_mcp.setup"
    )

if not TARGETPROCESS_TOKEN:
    raise RuntimeError(
        "TARGETPROCESS_TOKEN not set. Run: python -m targetprocess_mcp.setup"
    )

API_BASE = f"{TARGETPROCESS_URL.rstrip('/')}/api/v1"


def check_vpn() -> bool:
    """Check if VPN is connected (if required by configuration)."""
    if not VPN_REQUIRED:
        return True

    if not VPN_CHECK_HOSTS:
        return True

    import socket

    for host in VPN_CHECK_HOSTS:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((host, 443))
            sock.close()
            return True
        except Exception:
            try:
                socket.gethostbyname(host)
                return True
            except Exception:
                continue

    return False
