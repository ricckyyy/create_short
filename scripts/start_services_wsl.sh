#!/bin/bash
# WSL環境でOllamaとVOICEVOX Engineを起動するスクリプト

echo "🚀 サービス起動スクリプト"
echo "================================"

# Docker起動確認
if ! docker ps > /dev/null 2>&1; then
    echo "🐳 Dockerサービスを起動中..."
    
    # dockerグループに所属しているか確認
    if ! groups | grep -q docker; then
        echo "⚠️  dockerグループに所属していません"
        echo "   sudoパスワードが必要です..."
        sudo service docker start || {
            echo "❌ Docker起動失敗"
            exit 1
        }
    else
        # グループに所属している場合でもserviceコマンドにはsudoが必要
        sudo service docker start 2>/dev/null || service docker start || {
            echo "❌ Docker起動失敗"
            exit 1
        }
    fi
    sleep 5
fi

# VOICEVOX Engine起動確認
if ! docker ps | grep -q voicevox; then
    echo "🎙️ VOICEVOX Engineを起動中..."
    docker start voicevox 2>/dev/null || \
    docker run -d --name voicevox -p 50021:50021 voicevox/voicevox_engine:cpu-ubuntu20.04-latest
    sleep 5
    echo "✅ VOICEVOX Engine起動完了: http://127.0.0.1:50021"
else
    echo "✅ VOICEVOX Engine は既に起動しています"
fi

# Ollama起動確認
export OLLAMA_MODELS=/mnt/g/ollama/models
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "🦙 Ollamaを起動中..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 5
    echo "✅ Ollama起動完了: http://127.0.0.1:11434"
else
    echo "✅ Ollama は既に起動しています"
fi

echo "================================"
echo "✅ すべてのサービスが起動しました"
echo ""
echo "【確認コマンド】"
echo "  VOICEVOX: curl http://127.0.0.1:50021/speakers | head -20"
echo "  Ollama:   curl http://127.0.0.1:11434/api/tags"
