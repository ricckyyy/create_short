#!/bin/bash

# GitHub Copilot トークン取得・設定スクリプト

echo "🤖 GitHub Copilot 台本生成セットアップ"
echo "========================================"
echo ""

# GitHub CLI がインストールされているか確認
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI が見つかりました"
    echo ""
    
    # ログイン確認
    if gh auth status &> /dev/null; then
        echo "✅ GitHub にログイン済み"
        echo ""
        
        # トークン取得
        echo "📝 GitHub トークンを取得中..."
        TOKEN=$(gh auth token)
        
        if [ -n "$TOKEN" ]; then
            echo "✅ トークン取得成功"
            echo ""
            
            # 環境変数設定
            echo "📌 環境変数を設定します..."
            echo ""
            echo "以下のコマンドを実行してください:"
            echo ""
            echo "export GITHUB_TOKEN=\"$TOKEN\""
            echo ""
            echo "永続化する場合:"
            echo "echo 'export GITHUB_TOKEN=\"$TOKEN\"' >> ~/.bashrc"
            echo "source ~/.bashrc"
            echo ""
            
            # 自動設定オプション
            read -p "今すぐ ~/.bashrc に追加しますか？ (y/n): " answer
            
            if [ "$answer" = "y" ]; then
                echo "export GITHUB_TOKEN=\"$TOKEN\"" >> ~/.bashrc
                export GITHUB_TOKEN="$TOKEN"
                echo ""
                echo "✅ ~/.bashrc に追加しました"
                echo "✅ 現在のセッションでも有効化しました"
                echo ""
                echo "次回から自動的に使用されます"
            else
                echo ""
                echo "手動で設定してください"
            fi
            
            echo ""
            echo "🎬 動画生成テスト:"
            echo "./scripts/test_generation.sh"
        else
            echo "❌ トークン取得失敗"
        fi
    else
        echo "❌ GitHub にログインしていません"
        echo ""
        echo "以下のコマンドでログインしてください:"
        echo "gh auth login"
    fi
else
    echo "⚠️  GitHub CLI がインストールされていません"
    echo ""
    echo "手動でトークンを取得してください:"
    echo "1. https://github.com/settings/tokens にアクセス"
    echo "2. 'Generate new token (classic)' をクリック"
    echo "3. スコープ: read:user, user:email を選択"
    echo "4. トークンをコピー"
    echo "5. export GITHUB_TOKEN=\"your-token\" を実行"
    echo ""
    echo "または GitHub CLI をインストール:"
    echo "https://cli.github.com/"
fi

echo ""
echo "========================================"
echo "📚 詳細: docs/SCRIPT_GENERATION.md"
