#!/usr/bin/env python3
"""
TikTok自動投稿モジュール
TikTok Content Posting API を使用した動画アップロード
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
from config import UPLOAD_HISTORY_DIR, UPLOAD_QUEUE_DIR

# TikTok API設定
TIKTOK_API_BASE_URL = "https://open.tiktokapis.com"
TIKTOK_API_VERSION = "v2"

class TikTokUploader:
    """TikTok動画アップロードクラス"""
    
    def __init__(self, access_token):
        """
        初期化
        
        Args:
            access_token: TikTok API アクセストークン
        """
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def upload_video(self, video_path, title, description, privacy_level="PUBLIC_TO_EVERYONE", 
                     disable_duet=False, disable_comment=False, disable_stitch=False):
        """
        動画をTikTokにアップロード
        
        Args:
            video_path: 動画ファイルのパス
            title: 動画タイトル（最大150文字）
            description: 動画説明（最大2200文字）
            privacy_level: 公開設定 ("PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "SELF_ONLY")
            disable_duet: デュエット無効化
            disable_comment: コメント無効化
            disable_stitch: スティッチ無効化
        
        Returns:
            dict: アップロード結果
        """
        try:
            print(f"📤 TikTokアップロード開始: {Path(video_path).name}")
            
            # Step 1: 動画初期化（チャンクアップロード用のURLを取得）
            init_response = self._initialize_upload(
                title=title,
                privacy_level=privacy_level,
                disable_duet=disable_duet,
                disable_comment=disable_comment,
                disable_stitch=disable_stitch
            )
            
            if not init_response.get("data"):
                raise Exception(f"初期化失敗: {init_response}")
            
            publish_id = init_response["data"]["publish_id"]
            upload_url = init_response["data"]["upload_url"]
            
            print(f"✅ 初期化完了 (publish_id: {publish_id})")
            
            # Step 2: 動画ファイルをアップロード
            self._upload_video_file(upload_url, video_path)
            print(f"✅ ファイルアップロード完了")
            
            # Step 3: 投稿を確定
            publish_response = self._publish_video(publish_id)
            
            if publish_response.get("error"):
                raise Exception(f"投稿失敗: {publish_response['error']['message']}")
            
            print(f"🎉 TikTok投稿完了！")
            
            # 投稿履歴を保存
            self._save_upload_history(video_path, title, description, publish_response)
            
            return {
                "success": True,
                "publish_id": publish_id,
                "response": publish_response
            }
            
        except Exception as e:
            error_msg = f"TikTokアップロードエラー: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def _initialize_upload(self, title, privacy_level, disable_duet, disable_comment, disable_stitch):
        """動画アップロードの初期化"""
        url = f"{TIKTOK_API_BASE_URL}/{TIKTOK_API_VERSION}/post/publish/inbox/video/init/"
        
        data = {
            "post_info": {
                "title": title[:150],  # 最大150文字
                "privacy_level": privacy_level,
                "disable_duet": disable_duet,
                "disable_comment": disable_comment,
                "disable_stitch": disable_stitch,
                "video_cover_timestamp_ms": 1000
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": Path(video_path).stat().st_size,
                "chunk_size": 10485760,  # 10MB
                "total_chunk_count": 1
            }
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
    
    def _upload_video_file(self, upload_url, video_path):
        """動画ファイルをアップロード"""
        with open(video_path, 'rb') as video_file:
            video_data = video_file.read()
        
        headers = {
            "Content-Type": "video/mp4",
            "Content-Length": str(len(video_data))
        }
        
        response = requests.put(upload_url, headers=headers, data=video_data)
        
        if response.status_code not in [200, 201]:
            raise Exception(f"ファイルアップロード失敗: {response.status_code} - {response.text}")
    
    def _publish_video(self, publish_id):
        """投稿を確定"""
        url = f"{TIKTOK_API_BASE_URL}/{TIKTOK_API_VERSION}/post/publish/status/fetch/"
        
        data = {
            "publish_id": publish_id
        }
        
        # 処理完了を待つ（最大30秒）
        max_attempts = 30
        for attempt in range(max_attempts):
            response = requests.post(url, headers=self.headers, json=data)
            result = response.json()
            
            if result.get("data", {}).get("status") == "PUBLISH_COMPLETE":
                return result
            
            print(f"⏳ 処理中... ({attempt + 1}/{max_attempts})")
            time.sleep(1)
        
        raise Exception("投稿処理がタイムアウトしました")
    
    def _save_upload_history(self, video_path, title, description, response):
        """投稿履歴を保存"""
        history_file = UPLOAD_HISTORY_DIR / f"tiktok_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        history_data = {
            "platform": "TikTok",
            "video_path": str(video_path),
            "title": title,
            "description": description,
            "uploaded_at": datetime.now().isoformat(),
            "response": response
        }
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
        
        print(f"📝 履歴保存: {history_file}")


def generate_tiktok_metadata(account_name, script_text):
    """
    TikTok用のメタデータ生成
    
    Args:
        account_name: アカウント名
        script_text: 台本テキスト
    
    Returns:
        dict: タイトル、説明、ハッシュタグ
    """
    
    # アカウント別のハッシュタグとテンプレート
    templates = {
        "心理テストラボ": {
            "title_prefix": "【心理テスト】",
            "description": "結果はどうでしたか？コメントで教えてください！\n\n#心理テスト #性格診断 #診断 #占い",
            "hashtags": ["心理テスト", "性格診断", "診断", "占い", "心理学", "自己分析"]
        },
        "闇夜の語り部": {
            "title_prefix": "【怖い話】",
            "description": "怖かったらいいねとフォローお願いします...\n\n#怖い話 #都市伝説 #ホラー #心霊",
            "hashtags": ["怖い話", "都市伝説", "ホラー", "心霊", "オカルト", "不思議"]
        },
        "映画紹介": {
            "title_prefix": "【映画紹介】",
            "description": "気になったらコメントで教えてください！\n\n#映画紹介 #映画レビュー #映画好き #おすすめ映画",
            "hashtags": ["映画紹介", "映画レビュー", "映画好き", "おすすめ映画", "映画", "洋画"]
        }
    }
    
    template = templates.get(account_name, templates["心理テストラボ"])
    
    # 台本の最初の行からタイトルを生成
    first_line = script_text.split('\n')[0].strip()
    title = f"{template['title_prefix']}{first_line[:50]}"
    
    return {
        "title": title,
        "description": template["description"],
        "hashtags": template["hashtags"]
    }


def upload_to_tiktok(video_path, account_name, script_text, access_token):
    """
    TikTokに動画をアップロード（簡易インターフェース）
    
    Args:
        video_path: 動画ファイルのパス
        account_name: アカウント名
        script_text: 台本テキスト
        access_token: TikTok APIアクセストークン
    
    Returns:
        dict: アップロード結果
    """
    
    # メタデータ生成
    metadata = generate_tiktok_metadata(account_name, script_text)
    
    # アップロード実行
    uploader = TikTokUploader(access_token)
    result = uploader.upload_video(
        video_path=video_path,
        title=metadata["title"],
        description=metadata["description"],
        privacy_level="PUBLIC_TO_EVERYONE",
        disable_comment=False
    )
    
    return result


# テスト実行
if __name__ == "__main__":
    print("TikTok自動投稿モジュール")
    print("=" * 60)
    print("\n⚠️  使用前に以下を準備してください:")
    print("1. TikTok Developer Portalでアプリを登録")
    print("2. Content Posting API のアクセス権限を取得")
    print("3. アクセストークンを取得")
    print("\n詳細: docs/TIKTOK_SETUP.md を参照")
