#!/bin/bash
# 最新の投稿用説明文を表示

DESCRIPTIONS_FILE="/home/rt/create_short/data/upload/latest_descriptions.txt"

if [ -f "$DESCRIPTIONS_FILE" ]; then
    cat "$DESCRIPTIONS_FILE"
else
    echo "❌ 説明文ファイルが見つかりません"
    echo "📝 動画生成後に自動作成されます"
    exit 1
fi
