#!/usr/bin/env python3
"""
GitHub Actions で生成された動画を自動ダウンロードするスクリプト
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

DOWNLOAD_DIR = Path("downloaded_videos")


def check_gh_cli():
    """GitHub CLIのインストールと認証をチェック"""
    try:
        subprocess.run(["gh", "auth", "status"], 
                      check=True, 
                      capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_latest_runs(limit=10):
    """最新のワークフロー実行を取得"""
    try:
        result = subprocess.run(
            ["gh", "run", "list", 
             "--limit", str(limit),
             "--json", "databaseId,displayTitle,status,conclusion,createdAt,workflowName"],
            check=True,
            capture_output=True,
            text=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ エラー: {e}")
        return []


def download_artifacts(run_id, output_dir=None):
    """指定されたRun IDのArtifactsをダウンロード"""
    if output_dir is None:
        output_dir = DOWNLOAD_DIR / f"run_{run_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📥 Run ID {run_id} のArtifactsをダウンロード中...")
    print(f"📁 保存先: {output_dir}")
    
    try:
        subprocess.run(
            ["gh", "run", "download", str(run_id), "-D", str(output_dir)],
            check=True
        )
        print(f"✅ ダウンロード完了: {output_dir}")
        
        # ダウンロードされたファイルをリスト
        print("\n📄 ダウンロードされたファイル:")
        for file in output_dir.rglob("*"):
            if file.is_file():
                size = file.stat().st_size / (1024 * 1024)  # MB
                print(f"  - {file.relative_to(output_dir)} ({size:.2f} MB)")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ダウンロード失敗: {e}")
        return False


def main():
    print("🎬 GitHub Actions 動画ダウンロードツール")
    print("=" * 50)
    print()
    
    # GitHub CLIチェック
    if not check_gh_cli():
        print("❌ GitHub CLI (gh) がインストールされていないか、認証されていません")
        print()
        print("インストール方法:")
        print("  macOS: brew install gh")
        print("  Windows: choco install gh")
        print("  Linux: https://github.com/cli/cli#installation")
        print()
        print("認証:")
        print("  gh auth login")
        sys.exit(1)
    
    # Run ID指定チェック
    if len(sys.argv) > 1:
        run_id = sys.argv[1]
        download_artifacts(run_id)
        return
    
    # 最新の実行を表示
    print("📊 最新のワークフロー実行:")
    print()
    
    runs = get_latest_runs()
    
    if not runs:
        print("❌ ワークフロー実行が見つかりませんでした")
        sys.exit(1)
    
    # 完了した実行のみをフィルタ
    completed_runs = [r for r in runs if r['status'] == 'completed']
    
    if not completed_runs:
        print("❌ 完了したワークフロー実行が見つかりませんでした")
        sys.exit(1)
    
    # 実行をリスト表示
    for idx, run in enumerate(completed_runs, 1):
        status_icon = "✅" if run['conclusion'] == 'success' else "❌"
        created_at = datetime.fromisoformat(run['createdAt'].replace('Z', '+00:00'))
        print(f"{idx}. {status_icon} [{run['databaseId']}] {run['displayTitle']}")
        print(f"   ワークフロー: {run['workflowName']}")
        print(f"   日時: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    # ユーザー選択
    try:
        choice = input("ダウンロードする番号を入力してください (1-{}): ".format(len(completed_runs)))
        choice_idx = int(choice) - 1
        
        if 0 <= choice_idx < len(completed_runs):
            run_id = completed_runs[choice_idx]['databaseId']
            download_artifacts(run_id)
        else:
            print("❌ 無効な選択です")
            sys.exit(1)
    except (ValueError, KeyboardInterrupt):
        print("\n❌ キャンセルされました")
        sys.exit(1)


if __name__ == "__main__":
    main()
