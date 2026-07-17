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

echo "=== Installing Python libraries ==="
pip3 install oracledb boto3 edge-tts groq python-dotenv

echo "=== Setup complete! ==="
