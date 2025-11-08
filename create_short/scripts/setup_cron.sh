#!/bin/bash
# cron自動設定スクリプト

# プロジェクトルートに移動
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "⏰ 自動動画生成 cronジョブ設定"
echo "================================"
echo ""

# 現在のcron設定を確認
echo "📋 現在のcron設定:"
crontab -l 2>/dev/null || echo "   (設定なし)"
echo ""

echo "以下の設定を追加します:"
echo ""
echo "【毎日午前6時に自動生成】"
echo "0 12 * * * $PROJECT_ROOT/scripts/run_daily.sh >> $PROJECT_ROOT/data/logs/cron/cron_output.log 2>&1"
echo ""

read -p "この設定を追加しますか？ (y/n): " answer

if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    # 既存のcron設定を取得
    crontab -l 2>/dev/null > /tmp/current_cron
    
    # 重複チェック
    if grep -q "run_daily.sh" /tmp/current_cron 2>/dev/null; then
        echo ""
        echo "⚠️  既に設定が存在します。上書きしますか？ (y/n): "
        read overwrite
        if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
            echo "キャンセルしました"
            exit 0
        fi
        # 既存の設定を削除
        grep -v "run_daily.sh" /tmp/current_cron > /tmp/new_cron
    else
        cp /tmp/current_cron /tmp/new_cron
    fi
    
    # 新しい設定を追加
    echo "0 6 * * * $PROJECT_ROOT/scripts/run_daily.sh >> $PROJECT_ROOT/data/logs/cron/cron_output.log 2>&1" >> /tmp/new_cron
    
    # cronに設定
    crontab /tmp/new_cron
    
    echo ""
    echo "✅ cron設定完了！"
    echo ""
    echo "📋 設定内容:"
    crontab -l | grep "run_daily.sh"
    echo ""
    echo "📅 次回実行予定: 明日 午前6時"
    echo ""
    echo "💡 ヒント:"
    echo "  - 設定確認: crontab -l"
    echo "  - 設定削除: crontab -e で該当行を削除"
    echo "  - ログ確認: tail -f $PROJECT_ROOT/data/logs/cron/cron_output.log"
    echo ""
    
    # クリーンアップ
    rm /tmp/current_cron /tmp/new_cron 2>/dev/null
    
else
    echo ""
    echo "キャンセルしました"
    echo ""
    echo "💡 手動設定する場合:"
    echo "   1. crontab -e"
    echo "   2. 以下を追加:"
    echo "      0 6 * * * $PROJECT_ROOT/scripts/run_daily.sh >> $PROJECT_ROOT/data/logs/cron/cron_output.log 2>&1"
    echo ""
fi

echo "================================"
echo ""
echo "📖 詳細は docs/AUTOMATION_GUIDE.md を参照してください"
