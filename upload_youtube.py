#!/usr/bin/env python3
"""
YouTube Shorts 自動アップロードスクリプト
"""

import os
import pickle
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

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

#心理テスト #性格診断 #Shorts
            """.strip(),
            "tags": [
                "心理テスト", "性格診断", "心理学", "診断テスト",
                "性格", "自己分析", "占い", "心理",
                "Shorts", "ショート動画"
            ]
        },
        "闇夜の語り部": {
            "title_prefix": "【怖い話】",
            "description": """
🌙 闇夜の語り部です

今宵も不気味な物語をお届けします...
怖がりな方は、明るい場所でご視聴ください👻

#怖い話 #都市伝説 #Shorts
            """.strip(),
            "tags": [
                "怖い話", "都市伝説", "ホラー", "心霊",
                "オカルト", "恐怖", "ミステリー", "不思議",
                "Shorts", "ショート動画"
            ]
        },
        "映画紹介": {
            "title_prefix": "【映画紹介】",
            "description": """
🎬 映画好きのための1分レビュー

この映画、本当に面白いです！
気になったら観てみてください🍿

#映画紹介 #映画レビュー #Shorts
            """.strip(),
            "tags": [
                "映画紹介", "映画レビュー", "映画", "おすすめ映画",
                "洋画", "邦画", "名作", "映画好き",
                "Shorts", "ショート動画"
            ]
        }
    }
    
    template = templates.get(account_name, templates["心理テストラボ"])
    
    # タイトル生成（台本の最初の行を使用）
    first_line = script.split('\n')[0] if script else "必見"
    title = f"{template['title_prefix']}{first_line[:30]}"
    
    return {
        "title": title,
        "description": template["description"],
        "tags": template["tags"]
    }


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
