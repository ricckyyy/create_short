#!/usr/bin/env python3
"""
毎日自動実行される動画生成スクリプト
台本生成 → 動画生成を一括処理
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from generate_script import generate_all_scripts
from create_movie import generate_voice, create_video_with_keywords
from config import (
    init_directories, 
    get_video_path, 
    get_audio_path,
    get_script_path,
    LOGS_GENERATION_DIR,
    SCRIPTS_HISTORY_DIR,
    UPLOAD_DIR,
    PEXELS_API_KEY,
    ACCOUNTS,
    cleanup_temp_files
)
from upload_youtube import upload_video, generate_metadata
from db_manager import init_database, add_video

# ディレクトリ初期化
init_directories()
init_database()

def log_message(message):
    """ログ出力とファイル保存"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    
    # ログファイルに追記
    log_file = LOGS_GENERATION_DIR / f"generation_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")


def save_latest_descriptions():
    """最新のメタデータを読みやすい形式でファイルに保存（日付ごと）"""
    # 日付ごとのファイル名
    date_str = datetime.now().strftime('%Y%m%d')
    output_file = UPLOAD_DIR / f"descriptions_{date_str}.txt"
    
    # 最新版へのシンボリックリンク用
    latest_link = UPLOAD_DIR / "latest_descriptions.txt"
    
    content = []
    content.append("=" * 70)
    content.append("📝 YouTube/TikTok 投稿用説明文")
    content.append("=" * 70)
    content.append("")
    content.append("💡 以下をコピーして投稿画面の説明欄に貼り付けてください")
    content.append("")
    content.append("")
    
    # 各アカウントのメタデータを取得
    for account_name, account_info in ACCOUNTS.items():
        slug = account_info["slug"]
        
        # このアカウントの最新メタデータを検索
        metadata_files = sorted(
            SCRIPTS_HISTORY_DIR.glob(f"metadata_{slug}_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if metadata_files:
            with open(metadata_files[0], "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            content.append("━" * 70)
            content.append(f"🎬 {account_name}")
            content.append("━" * 70)
            content.append("")
            
            # タイトルを追加
            title = metadata.get("title", "無題")
            content.append(f"📺 {title}")
            content.append("")
            
            content.append(metadata.get("description", ""))
            content.append("")
            
            tags = metadata.get("tags", [])
            if tags:
                # タグを #付きハッシュタグ形式に変換
                hashtags = " ".join([f"#{tag}" if not tag.startswith('#') else tag for tag in tags])
                content.append(hashtags)
            
            content.append("")
            content.append("━" * 70)
            content.append("")
            content.append("")
    
    content.append("📋 使い方:")
    content.append("1. 各アカウントの説明文をコピー")
    content.append("2. YouTube/TikTokの投稿画面の説明欄に貼り付け")
    content.append("")
    content.append(f"📅 生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    
    # ファイルに保存
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(content))
    
    # 最新版へのシンボリックリンクを作成/更新
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    try:
        latest_link.symlink_to(output_file.name)
    except Exception:
        # Windows等でシンボリックリンクが作れない場合はコピー
        import shutil
        shutil.copy2(output_file, latest_link)
    
    return output_file


def generate_daily_videos():
    """日次動画生成処理"""
    try:
        log_message("="*60)
        log_message("🚀 日次動画生成バッチ開始")
        log_message("="*60)
        
        # Step 1: AI台本生成
        log_message("\n📝 Step 1: AI台本生成")
        
        # タイムスタンプを一度だけ生成
        date_str = datetime.now().strftime('%Y%m%d')
        timestamp = datetime.now().strftime('%H%M%S')
        
        accounts_data = generate_all_scripts(timestamp)
        
        # Step 2: 各アカウントの動画生成
        log_message("\n🎬 Step 2: 動画生成")
        
        success_count = 0
        error_count = 0
        
        for acc in accounts_data:
            try:
                log_message(f"\n{'='*60}")
                log_message(f"🎥 {acc['name']} 処理開始")
                log_message(f"{'='*60}")
                
                script_lines = [line.strip() for line in acc["script"].split("\n") if line.strip()]
                
                # アカウント設定取得
                account_config = ACCOUNTS.get(acc["name"], {})
                speaker_index = account_config.get("voice_speaker", 1)
                pitch = account_config.get("voice_pitch", 0)
                
                # 音声生成（タイムスタンプ付き）
                log_message(f"🎙️ 音声生成中...")
                audio_path = get_audio_path(acc["name"], date_str, timestamp)
                voice_file = generate_voice(
                    acc["script"], 
                    speaker_index=speaker_index, 
                    pitch=pitch, 
                    speed=1.0, 
                    filename=str(audio_path)
                )
                log_message(f"✅ 音声生成完了: {voice_file}")
                
                # 動画生成（タイムスタンプ付き）
                log_message(f"🎬 動画生成中...")
                video_path = get_video_path(acc["name"], date_str, timestamp, status="draft")
                create_video_with_keywords(
                    script_lines, 
                    acc["keywords"], 
                    PEXELS_API_KEY, 
                    voice_file, 
                    output_file=str(video_path)
                )
                log_message(f"✅ 動画生成完了: {video_path}")
                
                # メタデータ生成（タイトル・説明文・ハッシュタグ）
                log_message(f"📊 メタデータ生成中...")
                metadata = generate_metadata(acc["name"], acc["script"])
                
                # メタデータをファイルに保存（タイムスタンプ付き）
                metadata_file = SCRIPTS_HISTORY_DIR / f"metadata_{acc['slug']}_{date_str}_{timestamp}.json"
                with open(metadata_file, "w", encoding="utf-8") as f:
                    json.dump({
                        "title": metadata["title"],
                        "description": metadata["description"],
                        "tags": metadata["tags"],
                        "video_path": str(video_path),
                        "account": acc["name"],
                        "date": date_str
                    }, f, ensure_ascii=False, indent=2)
                log_message(f"✅ メタデータ保存: {metadata_file}")
                log_message(f"   タイトル: {metadata['title']}")
                log_message(f"   タグ数: {len(metadata['tags'])}")
                
                # データベースに動画情報を記録
                log_message(f"💾 データベースに記録中...")
                video_id = add_video(
                    account_name=acc["name"],
                    video_path=video_path,
                    script_content=acc["script"],
                    keywords=acc["keywords"],
                    title=metadata["title"],
                    description=metadata["description"]
                )
                log_message(f"✅ DB記録完了 (ID: {video_id})")
                
                # YouTube アップロード
                log_message(f"📤 YouTube アップロード中...")
                try:
                    upload_result = upload_video(
                        video_path=str(video_path),
                        title=metadata["title"],
                        description=metadata["description"],
                        tags=metadata["tags"],
                        privacy_status="public"  # 本番環境では public
                    )
                    log_message(f"✅ アップロード完了: {upload_result['url']}")
                    log_message(f"   動画ID: {upload_result['video_id']}")
                except Exception as upload_error:
                    log_message(f"⚠️  アップロード失敗（動画は生成済み）: {str(upload_error)}")
                    # アップロード失敗でも動画生成は成功とカウント
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                log_message(f"❌ {acc['name']} 生成エラー: {str(e)}")
                import traceback
                log_message(traceback.format_exc())
        
        # 一時ファイルをクリーンアップ
        log_message("\n🧹 一時ファイルをクリーンアップ中...")
        cleanup_temp_files()
        
        # 結果サマリー
        log_message("\n" + "="*60)
        log_message("📊 生成結果サマリー")
        log_message("="*60)
        log_message(f"✅ 成功: {success_count} 件")
        log_message(f"❌ 失敗: {error_count} 件")
        log_message(f"📅 実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        log_message("="*60)
        
        # メタデータ（投稿用説明文）を表示
        if success_count > 0:
            log_message("\n" + "="*60)
            log_message("📝 投稿用説明文を保存中...")
            log_message("="*60)
            descriptions_file = save_latest_descriptions()
            log_message(f"✅ 保存完了: {descriptions_file}")
            log_message(f"📄 確認: cat {descriptions_file}")
            log_message("="*60)
        
        # 成功時のステータスコード
        return 0 if error_count == 0 else 1
        
    except Exception as e:
        log_message(f"\n❌ 致命的エラー: {str(e)}")
        import traceback
        log_message(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit_code = generate_daily_videos()
    sys.exit(exit_code)
