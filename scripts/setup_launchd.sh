#!/bin/bash
# macOS launchd自動設定スクリプト

# プロジェクトルートに移動
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "⏰ macOS自動動画生成 launchd設定"
echo "================================"
echo ""

PLIST_FILE=~/Library/LaunchAgents/com.create-short.daily.plist

# 既存の設定を確認
if [ -f "$PLIST_FILE" ]; then
    echo "⚠️  既存の設定が見つかりました"
    echo ""
    read -p "既存の設定を上書きしますか？ (y/n): " answer
    if [ "$answer" != "y" ] && [ "$answer" != "Y" ]; then
        echo "キャンセルしました"
        exit 0
    fi
    
    # 既存のジョブを停止・削除
    launchctl unload "$PLIST_FILE" 2>/dev/null
    echo "✅ 既存の設定を削除しました"
fi

# plistファイルを作成
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.create-short.daily</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_ROOT/scripts/run_daily.sh</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>6</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>$PROJECT_ROOT/data/logs/cron/launchd_output.log</string>
    
    <key>StandardErrorPath</key>
    <string>$PROJECT_ROOT/data/logs/cron/launchd_error.log</string>
    
    <key>RunAtLoad</key>
    <false/>
    
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOF

echo ""
echo "✅ launchd設定ファイルを作成しました"
echo "📁 場所: $PLIST_FILE"
echo ""

# ログディレクトリを作成
mkdir -p "$PROJECT_ROOT/data/logs/cron"

# launchdに登録
launchctl load "$PLIST_FILE"

echo "✅ launchd設定完了！"
echo ""
echo "📋 設定内容:"
echo "  - 実行時刻: 毎日午前6時"
echo "  - スクリプト: $PROJECT_ROOT/scripts/run_daily.sh"
echo "  - ログ: $PROJECT_ROOT/data/logs/cron/"
echo ""
echo "💡 管理コマンド:"
echo "  - 設定確認: launchctl list | grep create-short"
echo "  - 手動実行: launchctl start com.create-short.daily"
echo "  - 停止: launchctl unload $PLIST_FILE"
echo "  - 再開: launchctl load $PLIST_FILE"
echo "  - ログ確認: tail -f $PROJECT_ROOT/data/logs/cron/launchd_output.log"
echo ""
echo "================================"
