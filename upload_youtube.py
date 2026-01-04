#!/usr/bin/env python3
"""
YouTube Shorts 自動アップロードスクリプト
"""

import os
import pickle
import sys
import re
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Ollama APIを使用する場合
try:
    import requests
    USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() not in ("false", "0", "no")
    OLLAMA_API_URL = "http://127.0.0.1:11434/api/chat"
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma2:9b")
except ImportError:
    USE_OLLAMA = False

# YouTube API スコープ
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# 認証ファイルのパス
PROJECT_ROOT = Path(__file__).parent
CLIENT_SECRETS_FILE = PROJECT_ROOT / "client_secrets.json"
TOKEN_FILE = PROJECT_ROOT / "token.pickle"


def get_authenticated_service():
    """
    YouTube API の認証済みサービスを取得
    """
    credentials = None
    
    # 既存のトークンファイルを確認
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as token:
            credentials = pickle.load(token)
    
    # トークンが無効または存在しない場合
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            # トークンをリフレッシュ
            credentials.refresh(Request())
        else:
            # 新規認証
            if not CLIENT_SECRETS_FILE.exists():
                raise FileNotFoundError(
                    f"client_secrets.json が見つかりません: {CLIENT_SECRETS_FILE}\n"
                    f"docs/YOUTUBE_API_SETUP.md を参照してセットアップしてください。"
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRETS_FILE), SCOPES)
            credentials = flow.run_local_server(port=0)
        
        # トークンを保存
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(credentials, token)
    
    return build('youtube', 'v3', credentials=credentials)


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list = None,
    category_id: str = "22",  # 22 = People & Blogs
    privacy_status: str = "unlisted"  # "public", "private", "unlisted"
):
    """
    YouTube に動画をアップロード
    
    Args:
        video_path: アップロードする動画ファイルのパス
        title: 動画のタイトル
        description: 動画の説明文
        tags: タグのリスト
        category_id: カテゴリID（デフォルト: People & Blogs）
        privacy_status: 公開設定（public/private/unlisted）
    
    Returns:
        dict: アップロード結果（video_id, url など）
    """
    if tags is None:
        tags = []
    
    # 動画ファイルの存在確認
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")
    
    try:
        # YouTube API サービスを取得
        youtube = get_authenticated_service()
        
        # アップロード用のメタデータ
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False  # 子供向けではない
            }
        }
        
        # 動画ファイルのアップロード
        media = MediaFileUpload(
            video_path,
            mimetype='video/mp4',
            resumable=True,
            chunksize=1024*1024  # 1MB chunks
        )
        
        # アップロードリクエストの作成
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        # アップロード実行（進捗表示付き）
        print(f"📤 アップロード中: {os.path.basename(video_path)}")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"   進捗: {progress}%", end='\r')
        
        print(f"\n✅ アップロード完了!")
        
        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        result = {
            'video_id': video_id,
            'url': video_url,
            'title': title,
            'status': privacy_status
        }
        
        print(f"📺 動画ID: {video_id}")
        print(f"🔗 URL: {video_url}")
        
        return result
        
    except HttpError as e:
        error_message = f"YouTube API エラー: {e}"
        
        # クォータ超過エラーの場合
        if e.resp.status == 403:
            error_message += "\n⚠️  API クォータを超過した可能性があります（1日10,000ユニット制限）"
        
        raise Exception(error_message)


def generate_metadata(account_name: str, script: str = "") -> dict:
    """
    アカウント別の投稿メタデータを生成
    
    Args:
        account_name: アカウント名
        script: 台本テキスト（オプション）
    
    Returns:
        dict: title, description, tags
    """
    # アカウント別テンプレート
    templates = {
        "心理テストラボ": {
            "title_prefix": "【心理テスト】",
            "description": """
📊 心理テストラボへようこそ！

今回の心理テストで、あなたの隠れた性格が明らかに！
結果をコメントで教えてください👇
            """.strip(),
            "base_tags": [
                "心理テスト", "性格診断", "心理学", "診断テスト",
                "Shorts", "ショート動画"
            ]
        },
        "闇夜の語り部": {
            "title_prefix": "【怖い話】",
            "description": """
🌙 闇夜の語り部です

今宵も不気味な物語をお届けします...
怖がりな方は、明るい場所でご視聴ください👻
            """.strip(),
            "base_tags": [
                "怖い話", "都市伝説", "ホラー", "心霊",
                "Shorts", "ショート動画"
            ]
        },
        "映画紹介": {
            "title_prefix": "【映画紹介】",
            "description": """
🎬 映画好きのための1分レビュー

この映画、本当に面白いです！
気になったら観てみてください🍿
            """.strip(),
            "base_tags": [
                "映画紹介", "映画レビュー", "映画", "おすすめ映画",
                "Shorts", "ショート動画"
            ]
        }
    }
    
    template = templates.get(account_name, templates["心理テストラボ"])
    
    # タイトル生成（台本の最初の行を使用）
    first_line = script.split('\n')[0] if script else "必見"
    title = f"{template['title_prefix']}{first_line[:30]}"
    
    # 台本からタグを動的に生成
    tags = generate_tags_from_script(script, account_name, template["base_tags"])
    
    return {
        "title": title,
        "description": template["description"],
        "tags": tags
    }


def generate_tags_from_script(script: str, account_name: str, base_tags: list) -> list:
    """台本の内容から動的にタグを生成"""
    
    if not script:
        return base_tags
    
    print(f"🏷️ 台本からタグを生成中...")
    
    additional_tags = []
    
    # 映画紹介の場合、映画タイトルを抽出
    if account_name == "映画紹介":
        movie_match = re.search(r'『([^』]+)』', script)
        if movie_match:
            movie_title = movie_match.group(1).strip()
            
            # 映画タイトルをそのまま追加
            additional_tags.append(movie_title)
            print(f"   ✅ 映画タイトルタグ追加: {movie_title}")
            
            # 副題がある場合、メインタイトルだけも追加
            if ' ' in movie_title or '　' in movie_title:
                main_title = movie_title.split()[0]
                if main_title != movie_title and len(main_title) >= 2:
                    additional_tags.append(main_title)
                    print(f"   ✅ メインタイトルタグ追加: {main_title}")
    
    # キーワード抽出（ルールベース）
    keyword_tags = extract_keywords_from_script(script, account_name)
    if keyword_tags:
        additional_tags.extend(keyword_tags)
        print(f"   ✅ キーワード抽出: {', '.join(keyword_tags)}")
    
    # AIで関連タグを生成（Ollamaが使える場合）
    if USE_OLLAMA:
        ai_tags = generate_tags_with_ai(script, account_name)
        if ai_tags:
            additional_tags.extend(ai_tags)
    
    # ベースタグ + 追加タグ（重複削除＆最大15個まで）
    all_tags = base_tags + additional_tags
    unique_tags = []
    seen = set()
    for tag in all_tags:
        if tag.lower() not in seen:
            unique_tags.append(tag)
            seen.add(tag.lower())
    
    return unique_tags[:15]


def extract_keywords_from_script(script: str, account_name: str) -> list:
    """台本からルールベースでキーワードを抽出"""
    
    keywords = []
    
    # アカウント別のキーワード辞書
    keyword_dict = {
        "心理テストラボ": {
            "当たる|当たり": "的中",
            "性格|人格": "性格分析",
            "恋愛": "恋愛診断",
            "仕事|職業": "適職診断",
            "相性": "相性診断",
            "深層心理": "深層心理",
            "隠れた|本当の": "本性",
            "あなた": "自己分析",
        },
        "闇夜の語り部": {
            "怪談": "怪談",
            "心霊|幽霊|霊": "心霊現象",
            "呪い": "呪い",
            "廃墟": "廃墟",
            "都市伝説": "都市伝説",
            "実話": "実話",
            "謎": "ミステリー",
            "不気味|不思議": "怪奇現象",
        },
        "映画紹介": {
            "Netflix": "Netflix",
            "Amazon|アマゾン": "AmazonPrime",
            "サスペンス": "サスペンス",
            "ミステリー": "ミステリー",
            "感動": "感動",
            "泣ける": "泣ける",
            "ホラー": "ホラー映画",
            "アクション": "アクション",
            "恋愛": "恋愛映画",
        }
    }
    
    # アカウント別のパターンでマッチング
    patterns = keyword_dict.get(account_name, {})
    for pattern, tag in patterns.items():
        if re.search(pattern, script):
            keywords.append(tag)
    
    return keywords[:5]


def generate_tags_with_ai(script: str, account_name: str) -> list:
    """AIを使って台本から関連タグを生成"""
    
    if not USE_OLLAMA:
        print("   ℹ️ AI機能が無効です（Ollama未起動）")
        return []
    
    prompt = f"""以下の{account_name}向けの台本から、YouTubeショート動画に最適なタグ（ハッシュタグ）を5-8個生成してください。

【台本】
{script}

【要件】
- 台本の内容に関連する具体的なタグ
- 日本語で簡潔に（2-5文字が理想）
- YouTubeで検索されやすいトレンドワード
- バズりやすいキーワードを優先
- ジャンル固有のタグも含める
- 5-8個のタグのみ

【出力形式】
タグのみを1行に1つずつ出力してください。説明や番号は不要です。

例:
衝撃
必見
知らなかった
"""

    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.5,  # 多様性を少し上げる
                    "num_predict": 150,
                }
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        tags_text = result.get("message", {}).get("content", "").strip()
        
        # タグを抽出
        tags = []
        for line in tags_text.split('\n'):
            line = line.strip()
            # 番号や不要な接頭辞を削除
            if line and any(line.startswith(prefix) for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.']):
                line = line.split('.', 1)[1].strip()
            # #, -, *, など記号を削除
            line = line.replace('#', '').replace('-', '').replace('*', '').strip()
            # 説明文を除外
            if line and len(line) <= 15 and not any(word in line for word in ['タグ:', '例:', '説明', '要件', 'YouTube']):
                tags.append(line)
        
        if tags:
            print(f"   ✅ AI生成タグ: {', '.join(tags[:8])}")
        return tags[:8]  # 最大8個
        
    except requests.exceptions.Timeout:
        print(f"   ⚠️ AI生成タイムアウト（60秒超過）")
        return []
    except Exception as e:
        print(f"   ⚠️ タグ生成エラー: {e}")
        return []
        return []


if __name__ == "__main__":
    # テスト用コード
    import config
    
    print("🧪 YouTube アップロードテスト")
    print("=" * 50)
    
    # テスト用動画を探す
    test_videos = list(config.VIDEOS_DRAFT_DIR.glob("*.mp4"))
    
    if not test_videos:
        print("❌ テスト用動画が見つかりません")
        print(f"   {config.VIDEOS_DRAFT_DIR} に動画を配置してください")
        sys.exit(1)
    
    test_video = test_videos[0]
    print(f"📹 テスト動画: {test_video.name}")
    
    # メタデータ生成
    account_name = "心理テストラボ"
    metadata = generate_metadata(account_name, "これはテスト動画です")
    
    print(f"\n📝 メタデータ:")
    print(f"   タイトル: {metadata['title']}")
    print(f"   タグ: {', '.join(metadata['tags'][:5])}...")
    
    # アップロード確認
    confirm = input("\n🚀 テストアップロードを実行しますか？ (y/N): ")
    
    if confirm.lower() == 'y':
        try:
            result = upload_video(
                video_path=str(test_video),
                title=metadata['title'],
                description=metadata['description'],
                tags=metadata['tags'],
                privacy_status="unlisted"  # テストは限定公開
            )
            print(f"\n✅ テスト成功！")
            print(f"   {result['url']}")
        except Exception as e:
            print(f"\n❌ エラー: {e}")
            sys.exit(1)
    else:
        print("キャンセルしました")
