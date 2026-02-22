#!/usr/bin/env python3
"""Setup script for TargetProcess MCP - configures credentials and stores in keychain."""

import os
import sys
import subprocess

KEYCHAIN_SERVICE = "targetprocess-mcp"
CONFIG_DIR = os.path.expanduser("~/.config/targetprocess-mcp")


def get_from_keychain(account: str) -> str | None:
    """Retrieve password from macOS Keychain."""
    try:
        result = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-s",
                KEYCHAIN_SERVICE,
                "-a",
                account,
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


def store_in_keychain(account: str, password: str) -> bool:
    """Store password in macOS Keychain."""
    try:
        existing = get_from_keychain(account)
        if existing:
            subprocess.run(
                [
                    "security",
                    "delete-generic-password",
                    "-s",
                    KEYCHAIN_SERVICE,
                    "-a",
                    account,
                ],
                capture_output=True,
            )
        subprocess.run(
            [
                "security",
                "add-generic-password",
                "-s",
                KEYCHAIN_SERVICE,
                "-a",
                account,
                "-w",
                password,
            ],
            capture_output=True,
            check=True,
        )
        return True
    except Exception as e:
        print(f"Error storing in keychain: {e}")
        return False


def prompt_for_credentials() -> tuple[str, str]:
    """Prompt user for TargetProcess URL and token."""
    print("=" * 50)
    print("TargetProcess MCP Setup")
    print("=" * 50)

    url = input(
        "TargetProcess URL (e.g., https://yourcompany.tpondemand.com): "
    ).strip()
    while not url:
        print("URL is required")
        url = input("TargetProcess URL: ").strip()

    token = get_from_keychain("api-token")
    if token:
        use_existing = (
            input("Found existing token in keychain. Use it? [Y/n]: ").strip().lower()
        )
        if use_existing != "n":
            return url, token

    token = input("API Token (from TargetProcess Settings > API): ").strip()
    while not token:
        print("Token is required")
        token = input("API Token: ").strip()

    return url, token


def prompt_for_vpn() -> tuple[bool, list[str]]:
    """Prompt for VPN configuration."""
    print("\n" + "=" * 50)
    print("VPN Configuration (optional)")
    print("=" * 50)

    vpn_required = input("Require VPN connection? [y/N]: ").strip().lower() == "y"

    check_hosts = []
    if vpn_required:
        print("\nEnter internal hosts to check VPN connectivity.")
        print("These should only be accessible when connected to your VPN.")
        print("Press Enter when done.")
        while True:
            host = input("  Host (or Enter to finish): ").strip()
            if not host:
                break
            check_hosts.append(host)

        if not check_hosts:
            print("Warning: No hosts specified. VPN check will be skipped.")

    return vpn_required, check_hosts


def main():
    os.makedirs(CONFIG_DIR, exist_ok=True)

    url, token = prompt_for_credentials()

    if store_in_keychain("api-token", token):
        print("Token stored securely in macOS Keychain")

    vpn_required, check_hosts = prompt_for_vpn()

    config_path = os.path.join(CONFIG_DIR, "config.py")
    with open(config_path, "w") as f:
        f.write(f'URL = "{url.rstrip("/")}"\n')
        if vpn_required:
            f.write(f"\n# VPN Configuration\n")
            f.write(f"VPN_REQUIRED = True\n")
            f.write(f"VPN_CHECK_HOSTS = {check_hosts!r}\n")

    print(f"\nConfiguration saved to {config_path}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("\n" + "=" * 50)
    print("Setup Complete!")
    print("=" * 50)
    print("\nTo add to Claude Code, run:")
    print(
        f"  claude mcp add targetprocess --transport stdio --scope user -- python -m targetprocess_mcp.server"
    )
    print("\nOr add manually to ~/.claude.json:")
    print(
        '  {"mcpServers": {"targetprocess": {"command": "python", "args": ["-m", "targetprocess_mcp.server"]}}}'
    )


if __name__ == "__main__":
    main()
