#!/usr/bin/env python3
"""
YouTube手動アップロード用メタデータ出力スクリプト
タイトルと説明文をコピペしやすい形式で表示
"""

import json
from pathlib import Path
from config import SCRIPTS_HISTORY_DIR, VIDEOS_DRAFT_DIR

def format_for_youtube(metadata_file: Path):
    """
    メタデータをYouTube手動アップロード用に整形
    """
    with open(metadata_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # タグをハッシュタグ形式に変換
    hashtags = " ".join([f"#{tag}" for tag in data["tags"]])
    
    # 説明文とハッシュタグを統合（コピペしやすく）
    description_with_tags = f"{data['description']}\n\n{hashtags}"
    
    # YouTube用フォーマット（説明文のみ）
    output = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 {data['account']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{description_with_tags}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return output


def main():
    """
    最新のメタデータを表示
    """
    # メタデータファイルを取得
    metadata_files = sorted(SCRIPTS_HISTORY_DIR.glob("metadata_*.json"))
    
    if not metadata_files:
        print("❌ メタデータファイルが見つかりません")
        print("   動画生成後に自動作成されます")
        return
    
    print("\n" + "="*70)
    print("📺 YouTube/TikTok 投稿用説明文")
    print("="*70)
    print("\n💡 以下をコピーして投稿画面の説明欄に貼り付けてください\n")
    
    # アカウント別にグループ化
    from config import ACCOUNTS
    
    # ACCOUNTS の順序で表示
    for account_name in ACCOUNTS.keys():
        # このアカウントのslugを取得
        slug = ACCOUNTS[account_name]["slug"]
        
        # slugでメタデータファイルを検索
        account_files = [f for f in metadata_files if slug in f.stem]
        
        if account_files:
            latest_file = sorted(account_files)[-1]  # 最新のファイル
            print(format_for_youtube(latest_file))
        else:
            print(f"\n⚠️ {account_name} のメタデータが見つかりません\n")
    
    print("\n📋 使い方:")
    print("1. 各アカウントの説明文をコピー")
    print("2. YouTube/TikTokの投稿画面の説明欄に貼り付け")
    print()


if __name__ == "__main__":
    main()
