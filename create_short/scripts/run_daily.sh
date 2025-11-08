#!/bin/bash
# 日次動画生成実行ラッパースクリプト
# cronから実行される

# プロジェクトルートに移動
cd "$(dirname "$0")/.."

# VOICEVOX Engineが起動していなければ起動
if ! tmux has-session -t voicevox 2>/dev/null; then
    echo "🎙️ VOICEVOX Engineを起動中..."
    tmux new-session -d -s voicevox 'cd ~/voicevox_engine-linux-cpu-x64-0.24.1/linux-cpu-x64 && ./run'
    sleep 5  # 起動待機
fi

#!/bin/bash

# 仮想環境のアクティベート

# 日次生成スクリプト実行
python3 daily_generation.py

# 実行結果を記録
echo "日次動画生成完了: $(date)" >> logs/cron_execution.log
