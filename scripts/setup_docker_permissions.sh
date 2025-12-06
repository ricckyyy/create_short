#!/bin/bash
# Dockerをsudoなしで実行できるよう設定

echo "🔧 Docker権限設定スクリプト"
echo "================================"

# ユーザーをdockerグループに追加
echo "ユーザーをdockerグループに追加中..."
sudo usermod -aG docker $USER

echo ""
echo "✅ 設定完了！"
echo ""
echo "【重要】変更を反映するには、WSLを再起動してください："
echo "  PowerShellから: wsl --shutdown"
echo "  その後: wsl"
echo ""
echo "再起動後、以下で確認できます："
echo "  groups | grep docker"
