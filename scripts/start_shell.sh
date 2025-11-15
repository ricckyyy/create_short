#!/bin/bash

# VOICEVOX Engine を新しいターミナルで起動（既に存在する場合はスキップ）
if ! tmux has-session -t voicevox 2>/dev/null; then
    tmux new-session -d -s voicevox 'cd ~/voicevox_engine-linux-cpu-x64-0.24.1/linux-cpu-x64 && ./run'
    # 5秒待つ
    sleep 1
fi

