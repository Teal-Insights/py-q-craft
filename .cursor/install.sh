#!/usr/bin/env bash
# Idempotent bootstrap for the Q-CRAFT Cloud Agent environment.
# Installs the uv package manager and the Quarto CLI (needed to render the
# documentation site), then syncs the project's Python environment.
set -euo pipefail

QUARTO_VERSION="1.10.18"

# uv manages the pinned Python toolchain and the project virtualenv.
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"

# Expose uv on the system PATH so every future shell can find it.
sudo ln -sf "$HOME/.local/bin/uv" /usr/local/bin/uv
sudo ln -sf "$HOME/.local/bin/uvx" /usr/local/bin/uvx

# Quarto renders the executable .qmd user-guide pages during `great-docs build`.
if ! command -v quarto >/dev/null 2>&1 || [ "$(quarto --version 2>/dev/null)" != "$QUARTO_VERSION" ]; then
  tmp="$(mktemp -d)"
  curl -sSL -o "$tmp/quarto.deb" \
    "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.deb"
  sudo dpkg -i "$tmp/quarto.deb"
  rm -rf "$tmp"
fi

# Install the pinned Python interpreter plus project, dev, and validation deps.
# The Windows-only validation dependency (pywin32) is guarded by an environment
# marker in pyproject.toml, so this resolves cleanly on Linux.
uv sync --group dev
