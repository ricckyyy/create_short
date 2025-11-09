from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from threading import Thread
from datetime import datetime
from pathlib import Path
from create_movie import generate_voice, create_video_with_keywords
from config import (
    init_directories,
    get_video_path,
    get_audio_path,
    VIDEOS_DRAFT_DIR,
    VIDEOS_PUBLISHED_DIR,
    SCRIPTS_HISTORY_DIR,
    UPLOAD_DIR,
    PEXELS_API_KEY,
    ACCOUNTS,
    cleanup_temp_files
)
from db_manager import (
    init_database,
    get_all_videos,
    update_video_metrics,
    get_video_by_path,
    get_performance_stats
)

app = Flask(__name__)
CORS(app)

# ディレクトリ初期化
init_directories()
init_database()

# 進捗状況を保存
progress_status = {
    "status": "idle",  # idle, processing, completed, error
    "message": "",
    "current_account": "",
    "progress": 0
}

def generate_video_background(account_data):
    """バックグラウンドで動画生成"""
    global progress_status
    try:
        progress_status["status"] = "processing"
        progress_status["current_account"] = account_data["name"]
        progress_status["message"] = f"{account_data['name']}の音声を生成中..."
        progress_status["progress"] = 30
        
        script_lines = [line.strip() for line in account_data["script"].split("\n") if line.strip()]
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # アカウント設定取得
        account_config = ACCOUNTS.get(account_data["name"], {})
        speaker_index = account_config.get("voice_speaker", 1)
        pitch = account_config.get("voice_pitch", 0)
        
        # 音声生成（新しいパス構造）
        audio_path = get_audio_path(account_data["name"], date_str)
        voice_file = generate_voice(
            account_data["script"], 
            speaker_index=speaker_index, 
            pitch=pitch, 
            speed=1.0, 
            filename=str(audio_path)
        )
        
        progress_status["message"] = f"{account_data['name']}の動画を生成中..."
        progress_status["message"] = f"{account_data['name']}の動画を生成中..."
        progress_status["progress"] = 60
        
        # 動画生成（新しいパス構造）
        video_path = get_video_path(account_data["name"], date_str, status="draft")
        create_video_with_keywords(
            script_lines, 
            account_data["keywords"], 
            PEXELS_API_KEY, 
            voice_file, 
            output_file=str(video_path)
        )
        
        progress_status["status"] = "completed"
        progress_status["message"] = f"{account_data['name']}の動画生成完了！"
        progress_status["progress"] = 100
        
        # 一時ファイルクリーンアップ
        cleanup_temp_files()
        
    except Exception as e:
        progress_status["status"] = "error"
        progress_status["message"] = f"エラー: {str(e)}"
        progress_status["progress"] = 0

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    """動画生成APIエンドポイント"""
    data = request.json
    
    account_data = {
        "name": data.get("name"),
        "script": data.get("script"),
        "keywords": data.get("keywords", []),
        "output": f"output/{data.get('name', 'video')}.mp4"
    }
    
    # バックグラウンドで動画生成開始
    thread = Thread(target=generate_video_background, args=(account_data,))
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started", "message": "動画生成を開始しました"})

@app.route('/api/progress')
def get_progress():
    """進捗状況取得"""
    return jsonify(progress_status)

@app.route('/api/download/<filename>')
def download(filename):
    """動画ダウンロード"""
    file_path = os.path.join('output', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

@app.route('/api/presets')
def get_presets():
    """プリセットアカウント情報取得"""
    presets = [
        {
            "name": "心理テストラボ",
            "description": "性格診断・心理テスト系",
            "sample_keywords": ["psychology", "personality test", "quiz", "thinking", "brain", "mind", "decision making", "psychology test", "personality", "self discovery"]
        },
        {
            "name": "闇夜の語り部",
            "description": "怖い話・都市伝説系",
            "sample_keywords": ["dark night", "mystery", "shadow", "haunted", "ghost story", "urban legend", "scary", "horror", "darkness", "supernatural"]
        },
        {
            "name": "映画紹介",
            "description": "映画レビュー・おすすめ系",
            "sample_keywords": ["mystery movie", "plot twist", "detective", "time", "memory loss", "thriller", "suspense film", "cinema", "movie review", "spoiler free"]
        }
    ]
    return jsonify(presets)

@app.route('/api/list-videos')
def list_videos():
    """生成済み動画一覧（新しいディレクトリ構造）"""
    videos = []
    
    # 下書きと投稿済みの両方をチェック
    for status, video_dir in [("draft", VIDEOS_DRAFT_DIR), ("published", VIDEOS_PUBLISHED_DIR)]:
        if video_dir.exists():
            for file in video_dir.glob("*.mp4"):
                videos.append({
                    "filename": file.name,
                    "size": file.stat().st_size,
                    "created": file.stat().st_ctime,
                    "status": status,
                    "path": str(file.relative_to(VIDEOS_DRAFT_DIR.parent))
                })
    
    # 作成日時でソート（新しい順）
    videos.sort(key=lambda x: x["created"], reverse=True)
    
    return jsonify(videos)

@app.route('/api/metadata')
def get_metadata():
    """最新のメタデータ取得"""
    metadata_list = []
    
    # 各アカウントの最新メタデータを取得
    for account_name, account_info in ACCOUNTS.items():
        slug = account_info["slug"]
        
        # このアカウントのメタデータファイルを検索
        metadata_files = sorted(
            SCRIPTS_HISTORY_DIR.glob(f"metadata_{slug}_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if metadata_files:
            # 最新のメタデータを読み込み
            with open(metadata_files[0], "r", encoding="utf-8") as f:
                metadata = json.load(f)
                metadata_list.append({
                    "account": account_name,
                    "slug": slug,
                    "title": metadata.get("title", ""),
                    "description": metadata.get("description", ""),
                    "tags": metadata.get("tags", []),
                    "date": metadata.get("date", ""),
                    "file": metadata_files[0].name
                })
    
    return jsonify(metadata_list)

@app.route('/api/analytics/videos')
def get_analytics_videos():
    """データベースから全動画情報を取得"""
    videos = get_all_videos()
    return jsonify(videos)

@app.route('/api/analytics/stats')
def get_analytics_stats():
    """パフォーマンス統計を取得"""
    stats = get_performance_stats()
    return jsonify(stats)

@app.route('/api/analytics/update', methods=['POST'])
def update_analytics():
    """再生数などのメトリクスを更新"""
    data = request.json
    video_path = data.get('video_path')
    views = data.get('views')
    likes = data.get('likes')
    comments = data.get('comments')
    retention_rate = data.get('retention_rate')
    
    # 動画IDを取得
    video = get_video_by_path(video_path)
    if not video:
        return jsonify({"error": "Video not found"}), 404
    
    # メトリクス更新
    update_video_metrics(
        video_id=video['id'],
        views=views,
        likes=likes,
        comments=comments,
        retention_rate=retention_rate
    )
    
    return jsonify({"success": True, "video_id": video['id']})

if __name__ == '__main__':
    init_directories()
    app.run(debug=True, host='0.0.0.0', port=5000)
