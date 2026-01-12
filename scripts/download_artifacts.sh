#!/bin/bash
# GitHub Actionsで生成された動画をダウンロードするスクリプト

set -e

# 色付き出力
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎬 GitHub Actions生成動画ダウンロードツール${NC}"
echo ""

# GitHub CLIのインストール確認
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️ GitHub CLI (gh) がインストールされていません${NC}"
    echo ""
    echo "インストール方法:"
    echo "  macOS: brew install gh"
    echo "  Windows: choco install gh"
    echo "  Linux: https://github.com/cli/cli#installation"
    exit 1
fi

# 認証確認
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️ GitHub CLIにログインしていません${NC}"
    echo ""
    echo "以下のコマンドでログインしてください:"
    echo "  gh auth login"
    exit 1
fi

# ダウンロード先ディレクトリ
DOWNLOAD_DIR="./downloaded_videos"
mkdir -p "$DOWNLOAD_DIR"

echo -e "${GREEN}✅ 最新のワークフロー実行を検索中...${NC}"

# PR番号を取得（オプション）
PR_NUMBER=""
if [ ! -z "$1" ]; then
    PR_NUMBER="$1"
    echo "PR #${PR_NUMBER} の動画をダウンロードします"
fi

# 最新のワークフロー実行からArtifactsをダウンロード
if [ -z "$PR_NUMBER" ]; then
    # 全ての実行から最新を取得
    echo "最新のワークフロー実行を取得中..."
    gh run list --limit 5 --json databaseId,status,conclusion,displayTitle,createdAt --jq '.[] | select(.status == "completed") | "\(.databaseId) \(.displayTitle) (\(.createdAt))"'
    
    echo ""
    echo -e "${YELLOW}ダウンロードしたいRun IDを入力してください (上記から選択):${NC}"
    read -r RUN_ID
    
    if [ -z "$RUN_ID" ]; then
        echo "Run IDが入力されませんでした"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}Run ID: ${RUN_ID} のArtifactsをダウンロード中...${NC}"
    gh run download "$RUN_ID" -D "$DOWNLOAD_DIR"
else
    # PR番号から最新を取得
    echo "PR #${PR_NUMBER} の最新実行を検索中..."
    RUN_ID=$(gh run list --json databaseId,headBranch,number --jq ".[] | select(.number == $PR_NUMBER) | .databaseId" | head -1)
    
    if [ -z "$RUN_ID" ]; then
        echo "PR #${PR_NUMBER} の実行が見つかりませんでした"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}Run ID: ${RUN_ID} のArtifactsをダウンロード中...${NC}"
    gh run download "$RUN_ID" -D "$DOWNLOAD_DIR"
fi

echo ""
echo -e "${GREEN}✅ ダウンロード完了！${NC}"
echo -e "${BLUE}📁 保存先: ${DOWNLOAD_DIR}${NC}"
echo ""
ls -lh "$DOWNLOAD_DIR"
