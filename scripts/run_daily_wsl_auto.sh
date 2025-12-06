#!/bin/bash
# WSL環境で動画生成を完全自動実行

cd /mnt/g/dev/create_short

# 環境変数設定
export OLLAMA_MODELS=/mnt/g/ollama/models
export OLLAMA_MODEL=gemma2:9b

# サービス起動
/mnt/g/dev/create_short/scripts/start_services_wsl.sh

# 10秒待機してサービスが完全に起動するのを待つ
echo "⏳ サービス起動を待機中..."
sleep 10

# 動画生成実行
python3 daily_generation.py
