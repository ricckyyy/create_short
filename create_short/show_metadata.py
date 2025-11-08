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
    
    # YouTube用フォーマット
    output = f"""
{'='*70}
🎬 {data['account']}
{'='*70}

📌 タイトル（コピーしてタイトル欄に貼り付け）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{data['title']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 説明文（コピーして説明欄に貼り付け）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{description_with_tags}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 動画ファイル: {data.get('video_path', 'N/A')}

{'='*70}
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
    print("📺 YouTube 手動アップロード用メタデータ")
    print("="*70)
    print("\n💡 以下をコピーしてYouTube投稿画面に貼り付けてください\n")
    
    # アカウント別にグループ化
    account_groups = {}
    for metadata_file in metadata_files:
        with open(metadata_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        account = data["account"]
        if account not in account_groups:
            account_groups[account] = []
        account_groups[account].append(metadata_file)
    
    # 各アカウントの最新メタデータを表示
    for account, files in account_groups.items():
        latest_file = sorted(files)[-1]  # 最新のファイル
        print(format_for_youtube(latest_file))
    
    print("\n📋 使い方:")
    print("1. 📌タイトル の枠内をコピー → YouTube投稿画面のタイトル欄に貼り付け")
    print("2. 📝説明文 の枠内をコピー → 説明欄に貼り付け（ハッシュタグ込み）")
    print("3. 動画ファイルのパスから動画をアップロード")
    print("\n💡 Tip: 枠線は含めずに、中身だけをコピーしてください")
    print()


if __name__ == "__main__":
    main()
