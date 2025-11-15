#!/bin/bash
# テスト実行スクリプト - API不要でテンプレートモードで動作確認

echo "🧪 自動生成システムのテスト実行"
echo "================================"
echo ""
echo "⚠️  このテストはAPIキーなしで実行されます"
echo "   ランダムテンプレートから台本が選択されます"
echo ""

# プロジェクトルートに移動
cd "$(dirname "$0")/.."
echo "📍 実行ディレクトリ: $(pwd)"
echo ""

# 仮想環境有効化

# VOICEVOX確認
echo "🔍 VOICEVOX Engine確認中..."
if ! curl -s http://127.0.0.1:50021/speakers > /dev/null 2>&1; then
    echo "⚠️  VOICEVOX Engineが起動していません"
    echo "🚀 起動しています..."
    
    if ! tmux has-session -t voicevox 2>/dev/null; then
        tmux new-session -d -s voicevox 'cd ~/voicevox_engine-linux-cpu-x64-0.24.1/linux-cpu-x64 && ./run'
        echo "⏳ 起動待機中（5秒）..."
        sleep 5
    fi
fi

echo "✅ VOICEVOX Engine 起動確認完了"
echo ""
echo "🎬 動画生成開始..."
echo "================================"
echo ""

# 生成実行
python3 daily_generation.py

# 結果表示
echo ""
echo "================================"
echo "📊 生成結果"
echo "================================"

if [ -d "output" ]; then
    echo ""
    echo "📹 生成された動画:"
    ls -lh output/*.mp4 2>/dev/null | tail -5 || echo "   動画が見つかりません"
    echo ""
fi

if [ -d "script_history" ]; then
    echo "📝 台本履歴:"
    ls -lt script_history/*.txt 2>/dev/null | head -5 || echo "   履歴が見つかりません"
    echo ""
fi

if [ -d "logs" ]; then
    echo "📄 最新ログ:"
    latest_log=$(ls -t logs/daily_generation_*.log 2>/dev/null | head -1)
    if [ -n "$latest_log" ]; then
        echo "   $latest_log"
        echo ""
        echo "📋 ログ末尾（最後の20行）:"
        tail -20 "$latest_log"
    else
        echo "   ログが見つかりません"
    fi
fi

echo ""
echo "================================"
echo "✅ テスト実行完了"
echo "================================"
