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

# Python実行（Homebrewのpython3を使用）
/opt/homebrew/bin/python3 daily_generation.py

# 実行結果を記録
if [ $? -eq 0 ]; then
    echo "✅ 日次動画生成完了: $(date)" >> data/logs/cron/execution.log
else
    echo "❌ 日次動画生成失敗: $(date)" >> data/logs/cron/execution.log
fi

echo "================================"
echo "完了: $(date)"
echo "================================"
