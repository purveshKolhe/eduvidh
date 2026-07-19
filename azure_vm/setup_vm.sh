#!/bin/bash
set -e

echo "=== Updating package list ==="
sudo apt-get update -y

echo "=== Installing Python3 pip ==="
sudo apt-get install -y python3-pip

echo "=== Installing Node.js 20.x ==="
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

echo "=== Installing FFmpeg and FFprobe ==="
sudo apt-get install -y ffmpeg

echo "=== Installing Chrome dependencies for Remotion ==="
sudo apt-get install -y \
  libnss3 \
  libnspr4 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libcups2 \
  libdrm2 \
  libxkbcommon0 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libgbm1 \
  libasound2 \
  libpango-1.0-0 \
  libcairo2

echo "=== Installing Google Chrome for the persistent local renderer ==="
if ! command -v google-chrome >/dev/null 2>&1; then
  curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list >/dev/null
  sudo apt-get update -y
  sudo apt-get install -y google-chrome-stable
fi

echo "=== Installing Python libraries ==="
pip3 install aiohttp fastapi modal oracledb boto3 edge-tts groq python-dotenv uvicorn

echo "=== Installing and bundling the persistent Remotion renderer ==="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTION_DIR="${SCRIPT_DIR}/../remotion-app"
(
  cd "${REMOTION_DIR}"
  npm ci
  npx remotion bundle src/index.ts --out-dir=bundled --log=error
)

echo "=== Setup complete! ==="
