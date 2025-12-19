#!/usr/bin/env python3
"""
既存の動画用にメタデータを再生成するスクリプト
"""

import json
from pathlib import Path
from upload_youtube import generate_metadata
from config import SCRIPTS_HISTORY_DIR, ACCOUNTS

# 11月9日06:00に生成された台本
scripts = {
    "心理テストラボ": "script_shinrigaku_20251109_060025.txt",
    "闇夜の語り部": "script_kowai_20251109_060028.txt",
    "映画紹介": "script_movie_20251109_060030.txt"
}

for account_name, script_file in scripts.items():
    # 台本を読み込み
    script_path = SCRIPTS_HISTORY_DIR / script_file
    if not script_path.exists():
        print(f"❌ {account_name}: 台本が見つかりません - {script_path}")
        continue
    
    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()
    
    # メタデータ生成
    print(f"🔄 {account_name} のメタデータを生成中...")
    metadata = generate_metadata(account_name, script)
    
    # メタデータをJSONに保存
    acc = ACCOUNTS[account_name]
    metadata_file = SCRIPTS_HISTORY_DIR / f"metadata_{acc['slug']}_20251109.json"
    
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump({
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata["tags"],
            "account": account_name,
            "date": "20251109",
            "script_file": script_file
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {account_name}: メタデータ保存 → {metadata_file.name}")
    print(f"   タイトル: {metadata['title']}")
    print()

print("✅ 全てのメタデータ生成完了")
print("📄 確認コマンド: python3 show_metadata.py")
