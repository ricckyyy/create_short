#!/bin/bash

# YouTube アップロードテストスクリプト

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# 仮想環境をアクティベート
source ~/myenv/bin/activate

echo "🧪 YouTube アップロードテスト"
echo "================================"
echo ""

# client_secrets.json の存在確認
if [ ! -f "client_secrets.json" ]; then
    echo "❌ client_secrets.json が見つかりません"
    echo ""
    echo "セットアップが必要です:"
    echo "1. docs/YOUTUBE_API_SETUP.md の手順に従って設定"
    echo "2. client_secrets.json をプロジェクトルートに配置"
    echo ""
    exit 1
fi

echo "✅ client_secrets.json 確認完了"
echo ""

# テスト実行
python upload_youtube.py
