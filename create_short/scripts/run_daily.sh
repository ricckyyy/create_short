#!/bin/bash
# 日次動画生成実行ラッパースクリプト
# launchd/cronから実行される

# プロジェクトルートに移動
cd "$(dirname "$0")/.."

echo "================================"
echo "🚀 日次動画生成開始: $(date)"
echo "================================"

# ログディレクトリ作成
mkdir -p data/logs/cron

# Homebrew PATHを追加（macOS用）
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# VOICEVOX Engineが起動していなければ起動
if ! tmux has-session -t voicevox 2>/dev/null; then
    echo "🎙️ VOICEVOX Engineを起動中..."
    tmux new-session -d -s voicevox 'cd ~/voicevox_engine-linux-cpu-x64-0.24.1/linux-cpu-x64 && ./run'
    sleep 5  # 起動待機
fi

# Ollama Engineが起動していなければ起動
if ! pgrep -x "ollama" > /dev/null; then
    echo "🦙 Ollama Engineを起動中..."
    ollama serve > /dev/null 2>&1 &
    sleep 3  # 起動待機
fi

# Python実行（環境に応じて自動検出）
if [ -f /opt/homebrew/bin/python3 ]; then
    # macOS (Homebrew)
    /opt/homebrew/bin/python3 daily_generation.py
else
    # Linux/WSL
    python3 daily_generation.py
fi

# 実行結果を記録
if [ $? -eq 0 ]; then
    echo "✅ 日次動画生成完了: $(date)" >> data/logs/cron/execution.log
else
    echo "❌ 日次動画生成失敗: $(date)" >> data/logs/cron/execution.log
fi

echo "================================"
echo "完了: $(date)"
echo "================================"

