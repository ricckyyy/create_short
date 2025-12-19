#!/usr/bin/env python3
"""
データベース管理モジュール
SQLiteを使用した動画パフォーマンスデータの管理
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from config import PROJECT_ROOT

# データベースファイルパス
DB_PATH = PROJECT_ROOT / "data" / "database" / "videos.db"


def get_connection():
    """データベース接続を取得"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 列名でアクセス可能に
    return conn


def init_database():
    """データベースとテーブルを初期化"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # videosテーブル: 動画情報と再生数
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT NOT NULL,
            video_path TEXT NOT NULL,
            script_content TEXT NOT NULL,
            keywords TEXT,
            title TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            retention_rate REAL DEFAULT 0.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # script_patternsテーブル: 成功パターン分析結果
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS script_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT NOT NULL,
            pattern_type TEXT NOT NULL,
            pattern_content TEXT NOT NULL,
            avg_views REAL DEFAULT 0.0,
            success_score REAL DEFAULT 0.0,
            sample_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # performance_logテーブル: パフォーマンス履歴
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER NOT NULL,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            retention_rate REAL DEFAULT 0.0,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ データベース初期化完了: {DB_PATH}")


def add_video(account_name, video_path, script_content, keywords=None, title=None, description=None):
    """新しい動画をデータベースに追加"""
    conn = get_connection()
    cursor = conn.cursor()
    
    keywords_str = json.dumps(keywords) if isinstance(keywords, list) else keywords
    
    cursor.execute("""
        INSERT INTO videos (account_name, video_path, script_content, keywords, title, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (account_name, str(video_path), script_content, keywords_str, title, description))
    
    video_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return video_id


def update_video_metrics(video_id, views=None, likes=None, comments=None, retention_rate=None):
    """動画のメトリクスを更新"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 更新するフィールドを動的に構築
    updates = []
    params = []
    
    if views is not None:
        updates.append("views = ?")
        params.append(views)
    if likes is not None:
        updates.append("likes = ?")
        params.append(likes)
    if comments is not None:
        updates.append("comments = ?")
        params.append(comments)
    if retention_rate is not None:
        updates.append("retention_rate = ?")
        params.append(retention_rate)
    
    if not updates:
        conn.close()
        return
    
    updates.append("last_updated = CURRENT_TIMESTAMP")
    params.append(video_id)
    
    query = f"UPDATE videos SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, params)
    
    # パフォーマンスログに記録
    if any([views, likes, comments, retention_rate]):
        cursor.execute("""
            INSERT INTO performance_log (video_id, views, likes, comments, retention_rate)
            VALUES (?, ?, ?, ?, ?)
        """, (video_id, views or 0, likes or 0, comments or 0, retention_rate or 0.0))
    
    conn.commit()
    conn.close()


def get_video_by_path(video_path):
    """動画パスから動画情報を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM videos WHERE video_path = ?", (str(video_path),))
    video = cursor.fetchone()
    conn.close()
    
    return dict(video) if video else None


def get_top_videos(account_name=None, limit=10, order_by="views"):
    """再生数の多い動画を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM videos"
    params = []
    
    if account_name:
        query += " WHERE account_name = ?"
        params.append(account_name)
    
    query += f" ORDER BY {order_by} DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    videos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return videos


def get_all_videos(account_name=None):
    """全動画を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if account_name:
        cursor.execute("SELECT * FROM videos WHERE account_name = ? ORDER BY created_at DESC", (account_name,))
    else:
        cursor.execute("SELECT * FROM videos ORDER BY created_at DESC")
    
    videos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return videos


def get_performance_stats(account_name=None):
    """パフォーマンス統計を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            account_name,
            COUNT(*) as total_videos,
            AVG(views) as avg_views,
            MAX(views) as max_views,
            AVG(retention_rate) as avg_retention,
            SUM(views) as total_views
        FROM videos
    """
    
    if account_name:
        query += " WHERE account_name = ?"
        cursor.execute(query + " GROUP BY account_name", (account_name,))
    else:
        query += " GROUP BY account_name"
        cursor.execute(query)
    
    stats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return stats


if __name__ == "__main__":
    # データベース初期化
    init_database()
    
    # テストデータ追加
    print("\n🧪 テストデータを追加...")
    video_id = add_video(
        account_name="心理テストラボ",
        video_path="data/videos/draft/test.mp4",
        script_content="テスト台本です",
        keywords=["psychology", "test"],
        title="【心理テスト】テスト動画"
    )
    print(f"✅ 動画追加完了 (ID: {video_id})")
    
    # メトリクス更新
    print("\n📊 メトリクスを更新...")
    update_video_metrics(video_id, views=1000, likes=50, comments=10, retention_rate=75.5)
    print("✅ 更新完了")
    
    # データ取得
    print("\n📋 データ取得...")
    videos = get_all_videos()
    for video in videos:
        print(f"  - {video['title']}: {video['views']} views")
    
    print("\n✅ データベーステスト完了")
