#!/usr/bin/env python3
"""
メタデータ生成テストスクリプト
"""

import json
from pathlib import Path
from upload_youtube import generate_metadata
from config import SCRIPTS_HISTORY_DIR

# 最新の台本ファイルを取得
script_files = sorted(SCRIPTS_HISTORY_DIR.glob("script_*_*.txt"))

if not script_files:
    print("❌ 台本ファイルが見つかりません")
    exit(1)

print("📝 メタデータ生成テスト")
print("=" * 60)

# アカウント名マッピング
account_mapping = {
    "shinrigaku": "心理テストラボ",
    "kowai": "闇夜の語り部",
    "movie": "映画紹介"
}

for script_file in script_files[-3:]:  # 最新3件
    # ファイル名からアカウント判定
    account_key = None
    for key in account_mapping.keys():
        if key in script_file.stem:
            account_key = key
            break
    
    if not account_key:
        continue
    
    account_name = account_mapping[account_key]
    
    # 台本読み込み
    with open(script_file, "r", encoding="utf-8") as f:
        script = f.read()
    
    print(f"\n🎬 {account_name}")
    print("-" * 60)
    print(f"📄 台本ファイル: {script_file.name}")
    
    # メタデータ生成
    metadata = generate_metadata(account_name, script)
    
    print(f"📺 タイトル: {metadata['title']}")
    print(f"📝 説明文:\n{metadata['description'][:150]}...")
    print(f"🏷️  タグ: {', '.join(metadata['tags'][:5])} など {len(metadata['tags'])}個")
    
    # メタデータをJSONで保存
    date_str = script_file.stem.split('_')[-1]
    metadata_file = SCRIPTS_HISTORY_DIR / f"metadata_{account_key}_{date_str}.json"
    
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump({
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata["tags"],
            "account": account_name,
            "script_file": script_file.name,
            "date": date_str
        }, f, ensure_ascii=False, indent=2)
    
    print(f"💾 保存先: {metadata_file.name}")

print("\n" + "=" * 60)
print("✅ メタデータ生成完了")
print(f"📁 保存場所: {SCRIPTS_HISTORY_DIR}")
