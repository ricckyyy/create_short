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
    PEXELS_API_KEY,
    ACCOUNTS,
    cleanup_temp_files
)

# ディレクトリ初期化
init_directories()

def log_message(message):
    """ログ出力とファイル保存"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    
    # ログファイルに追記
    log_file = LOGS_GENERATION_DIR / f"generation_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")


def generate_daily_videos():
    """日次動画生成処理"""
    try:
        log_message("="*60)
        log_message("🚀 日次動画生成バッチ開始")
        log_message("="*60)
        
        # Step 1: AI台本生成
        log_message("\n📝 Step 1: AI台本生成")
        accounts_data = generate_all_scripts()
        
        # Step 2: 各アカウントの動画生成
        log_message("\n🎬 Step 2: 動画生成")
        
        success_count = 0
        error_count = 0
        date_str = datetime.now().strftime('%Y%m%d')
        
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
                
                # 音声生成（新しいパス構造）
                log_message(f"🎙️ 音声生成中...")
                audio_path = get_audio_path(acc["name"], date_str)
                voice_file = generate_voice(
                    acc["script"], 
                    speaker_index=speaker_index, 
                    pitch=pitch, 
                    speed=1.0, 
                    filename=str(audio_path)
                )
                log_message(f"✅ 音声生成完了: {voice_file}")
                
                # 動画生成（新しいパス構造）
                log_message(f"🎬 動画生成中...")
                log_message(f"🎬 動画生成中...")
                video_path = get_video_path(acc["name"], date_str, status="draft")
                create_video_with_keywords(
                    script_lines, 
                    acc["keywords"], 
                    PEXELS_API_KEY, 
                    voice_file, 
                    output_file=str(video_path)
                )
                log_message(f"✅ 動画生成完了: {video_path}")
                
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
