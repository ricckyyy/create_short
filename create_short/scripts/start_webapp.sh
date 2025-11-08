#!/bin/bash

# プロジェクトルートに移動
cd "$(dirname "$0")/.."

# VOICEVOX Engine を新しいターミナルで起動（既に存在する場合はスキップ）
if ! tmux has-session -t voicevox 2>/dev/null; then
    echo "🎙️ VOICEVOX Engineを起動中..."
    tmux new-session -d -s voicevox 'cd ~/voicevox_engine-linux-cpu-x64-0.24.1/linux-cpu-x64 && ./run'
    echo "⏳ VOICEVOX Engineの起動を待機中..."
    sleep 3
fi

#!/bin/bash

# 仮想環境のアクティベート
source /home/rt/create_short/venv/bin/activate

# Flaskアプリの起動
echo "🚀 Webアプリを起動中..."
echo "📱 ブラウザで http://localhost:5000 を開いてください"
python app.py
