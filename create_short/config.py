"""
プロジェクト設定ファイル
全てのパスとディレクトリ構造を一元管理
"""

import os
from pathlib import Path

# プロジェクトルートディレクトリ
PROJECT_ROOT = Path(__file__).parent

# === ディレクトリ構造 ===

# データディレクトリ（全ての生成データを格納）
DATA_DIR = PROJECT_ROOT / "data"

# 動画出力
VIDEOS_DIR = DATA_DIR / "videos"
VIDEOS_PUBLISHED_DIR = VIDEOS_DIR / "published"     # 投稿済み
VIDEOS_DRAFT_DIR = VIDEOS_DIR / "draft"             # 下書き

# 音声ファイル（一時）
AUDIO_DIR = DATA_DIR / "audio"

# 台本管理
SCRIPTS_DIR = DATA_DIR / "scripts"
SCRIPTS_HISTORY_DIR = SCRIPTS_DIR / "history"       # 履歴
SCRIPTS_ARCHIVE_DIR = SCRIPTS_DIR / "archive"       # アーカイブ

# ログ
LOGS_DIR = DATA_DIR / "logs"
LOGS_GENERATION_DIR = LOGS_DIR / "generation"       # 生成ログ
LOGS_UPLOAD_DIR = LOGS_DIR / "upload"               # 投稿ログ
LOGS_CRON_DIR = LOGS_DIR / "cron"                   # cronログ

# ダウンロード済み素材（Pexels動画など）
ASSETS_DIR = DATA_DIR / "assets"
ASSETS_VIDEO_DIR = ASSETS_DIR / "video_clips"

# 投稿管理
UPLOAD_DIR = DATA_DIR / "upload"
UPLOAD_QUEUE_DIR = UPLOAD_DIR / "queue"             # 投稿待ち
UPLOAD_HISTORY_DIR = UPLOAD_DIR / "history"         # 投稿履歴

# === アカウント設定 ===

ACCOUNTS = {
    "心理テストラボ": {
        "slug": "shinrigaku",
        "description": "性格診断・心理テスト系",
        "voice_speaker": 1,      # ずんだもん
        "voice_pitch": 0,
        "video_prefix": "psychology"
    },
    "闇夜の語り部": {
        "slug": "kowai",
        "description": "怖い話・都市伝説系",
        "voice_speaker": 7,      # 青山龍星
        "voice_pitch": -0.5,
        "video_prefix": "horror"
    },
    "映画紹介": {
        "slug": "movie",
        "description": "映画レビュー・おすすめ系",
        "voice_speaker": 1,      # ずんだもん
        "voice_pitch": 0,
        "video_prefix": "cinema"
    }
}

# === API設定 ===

# Pexels API
PEXELS_API_KEY = "QqcFiUzxOsDiOYP3sUQyty0hKhTGdzgBQdPQ8nymB7Y1KaXkYocVkctS"

# VOICEVOX
VOICEVOX_API_URL = "http://127.0.0.1:50021"

# === ファイル命名規則 ===

def get_video_filename(account_name, date_str, status="draft"):
    """動画ファイル名を生成"""
    account = ACCOUNTS.get(account_name)
    if not account:
        return f"video_{date_str}.mp4"
    
    prefix = account["video_prefix"]
    slug = account["slug"]
    
    return f"{prefix}_{slug}_{date_str}.mp4"


def get_video_path(account_name, date_str, status="draft"):
    """動画ファイルのフルパスを取得"""
    filename = get_video_filename(account_name, date_str, status)
    
    if status == "published":
        return VIDEOS_PUBLISHED_DIR / filename
    else:
        return VIDEOS_DRAFT_DIR / filename


def get_audio_filename(account_name, date_str):
    """音声ファイル名を生成"""
    account = ACCOUNTS.get(account_name)
    slug = account["slug"] if account else "audio"
    return f"voice_{slug}_{date_str}.wav"


def get_audio_path(account_name, date_str):
    """音声ファイルのフルパスを取得"""
    filename = get_audio_filename(account_name, date_str)
    return AUDIO_DIR / filename


def get_script_filename(account_name, date_str, timestamp):
    """台本ファイル名を生成"""
    account = ACCOUNTS.get(account_name)
    slug = account["slug"] if account else "script"
    return f"script_{slug}_{date_str}_{timestamp}.txt"


def get_script_path(account_name, date_str, timestamp):
    """台本ファイルのフルパスを取得"""
    filename = get_script_filename(account_name, date_str, timestamp)
    return SCRIPTS_HISTORY_DIR / filename


# === ディレクトリ初期化 ===

def init_directories():
    """必要なディレクトリを全て作成"""
    directories = [
        DATA_DIR,
        VIDEOS_DIR,
        VIDEOS_PUBLISHED_DIR,
        VIDEOS_DRAFT_DIR,
        AUDIO_DIR,
        SCRIPTS_DIR,
        SCRIPTS_HISTORY_DIR,
        SCRIPTS_ARCHIVE_DIR,
        LOGS_DIR,
        LOGS_GENERATION_DIR,
        LOGS_UPLOAD_DIR,
        LOGS_CRON_DIR,
        ASSETS_DIR,
        ASSETS_VIDEO_DIR,
        UPLOAD_DIR,
        UPLOAD_QUEUE_DIR,
        UPLOAD_HISTORY_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ ディレクトリ構造を初期化しました")
    print(f"📁 データルート: {DATA_DIR}")


def cleanup_temp_files():
    """一時ファイルをクリーンアップ"""
    # 音声ファイルを削除
    if AUDIO_DIR.exists():
        for audio_file in AUDIO_DIR.glob("*.wav"):
            audio_file.unlink()
            print(f"🗑️ 削除: {audio_file.name}")
    
    # ダウンロード済み動画クリップを削除
    if ASSETS_VIDEO_DIR.exists():
        for video_file in ASSETS_VIDEO_DIR.glob("*.mp4"):
            video_file.unlink()
            print(f"🗑️ 削除: {video_file.name}")


if __name__ == "__main__":
    print("🔧 ディレクトリ構造設定")
    print("=" * 60)
    init_directories()
    print("\n📂 ディレクトリ構造:")
    print(f"""
data/
├── videos/
│   ├── draft/              # 下書き動画
│   └── published/          # 投稿済み動画
├── audio/                  # 一時音声ファイル
├── scripts/
│   ├── history/            # 台本履歴
│   └── archive/            # アーカイブ
├── logs/
│   ├── generation/         # 生成ログ
│   ├── upload/             # 投稿ログ
│   └── cron/               # cronログ
├── assets/
│   └── video_clips/        # ダウンロード素材
└── upload/
    ├── queue/              # 投稿待ち
    └── history/            # 投稿履歴
    """)
