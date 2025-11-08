#!/bin/bash

# YouTube手動アップロード用メタデータ表示スクリプト

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# 仮想環境をアクティベート

echo ""
echo "🎬 YouTube手動アップロード用メタデータ表示"
echo ""

# メタデータ表示
python show_metadata.py

echo ""
echo "📂 最新の動画ファイル:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ls -lht data/videos/draft/*.mp4 | head -3 | awk '{print "  " $9 " (" $5 ")"}'
echo ""
