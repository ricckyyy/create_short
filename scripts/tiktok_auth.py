#!/usr/bin/env python3
"""
TikTok OAuth 認証ヘルパー
アクセストークンを取得するための簡易スクリプト
"""

import requests
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys

# TikTok OAuth設定（環境変数またはここに直接設定）
CLIENT_KEY = "your_client_key_here"
CLIENT_SECRET = "your_client_secret_here"
REDIRECT_URI = "http://localhost:8000/callback"

class CallbackHandler(BaseHTTPRequestHandler):
    """OAuthコールバックを処理するHTTPハンドラー"""
    
    def do_GET(self):
        """GETリクエスト処理"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/callback':
            # 認証コードを取得
            query_params = parse_qs(parsed_path.query)
            code = query_params.get('code', [None])[0]
            
            if code:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(b"""
                    <html>
                    <head><title>TikTok OAuth Success</title></head>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h1 style="color: green;">&#10004; Authorization Successful!</h1>
                        <p>You can close this window and return to the terminal.</p>
                    </body>
                    </html>
                """)
                
                # アクセストークンを取得
                self.server.authorization_code = code
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                    <html>
                    <body>
                        <h1>Error: No authorization code received</h1>
                    </body>
                    </html>
                """)
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """ログ出力を抑制"""
        pass


def get_access_token(client_key, client_secret, redirect_uri):
    """
    TikTok アクセストークンを取得
    
    Args:
        client_key: TikTok Client Key
        client_secret: TikTok Client Secret
        redirect_uri: リダイレクトURI
    
    Returns:
        dict: トークン情報
    """
    
    print("=" * 60)
    print("🎵 TikTok OAuth 認証")
    print("=" * 60)
    
    # Step 1: 認証URLを生成
    scopes = ["video.upload", "video.publish"]
    auth_url = (
        f"https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={client_key}"
        f"&scope={','.join(scopes)}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
    )
    
    print("\n📱 Step 1: TikTokで認証")
    print(f"ブラウザが開きます...")
    print(f"認証URL: {auth_url}")
    
    # ブラウザで認証URLを開く
    webbrowser.open(auth_url)
    
    # Step 2: コールバックサーバーを起動
    print("\n⏳ Step 2: コールバックを待機中...")
    print(f"リダイレクトURI: {redirect_uri}")
    
    server = HTTPServer(('localhost', 8000), CallbackHandler)
    server.authorization_code = None
    
    # 1つのリクエストを処理したら終了
    server.handle_request()
    
    if not server.authorization_code:
        print("\n❌ 認証コードの取得に失敗しました")
        return None
    
    print(f"\n✅ 認証コード取得: {server.authorization_code[:20]}...")
    
    # Step 3: 認証コードをアクセストークンに交換
    print("\n🔑 Step 3: アクセストークンを取得中...")
    
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    token_data = {
        "client_key": client_key,
        "client_secret": client_secret,
        "code": server.authorization_code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }
    
    response = requests.post(token_url, data=token_data)
    
    if response.status_code != 200:
        print(f"\n❌ トークン取得エラー: {response.status_code}")
        print(response.text)
        return None
    
    token_info = response.json()
    
    if "access_token" not in token_info:
        print(f"\n❌ レスポンスにaccess_tokenがありません")
        print(token_info)
        return None
    
    print("\n" + "=" * 60)
    print("🎉 アクセストークン取得成功！")
    print("=" * 60)
    
    print(f"\n📋 以下を環境変数に設定してください:")
    print(f"\nexport TIKTOK_ACCESS_TOKEN=\"{token_info['access_token']}\"")
    
    if "refresh_token" in token_info:
        print(f"export TIKTOK_REFRESH_TOKEN=\"{token_info['refresh_token']}\"")
    
    if "expires_in" in token_info:
        print(f"\n⚠️  有効期限: {token_info['expires_in']}秒 ({token_info['expires_in']//3600}時間)")
    
    # トークン情報を保存
    import json
    from datetime import datetime
    from pathlib import Path
    
    token_file = Path("tiktok_token.json")
    token_info["obtained_at"] = datetime.now().isoformat()
    
    with open(token_file, 'w') as f:
        json.dump(token_info, f, indent=2)
    
    print(f"\n💾 トークン情報を保存: {token_file}")
    print(f"⚠️  このファイルは機密情報です！.gitignoreに追加されています")
    
    return token_info


if __name__ == "__main__":
    print("\n🔧 設定確認...")
    
    if CLIENT_KEY == "your_client_key_here" or CLIENT_SECRET == "your_client_secret_here":
        print("\n❌ エラー: CLIENT_KEY と CLIENT_SECRET を設定してください")
        print("\n設定方法:")
        print("1. このファイルを編集して CLIENT_KEY と CLIENT_SECRET を設定")
        print("2. または環境変数で設定:")
        print("   export TIKTOK_CLIENT_KEY='your_key'")
        print("   export TIKTOK_CLIENT_SECRET='your_secret'")
        sys.exit(1)
    
    # 環境変数からの読み込みをサポート
    import os
    client_key = os.getenv("TIKTOK_CLIENT_KEY", CLIENT_KEY)
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET", CLIENT_SECRET)
    
    token_info = get_access_token(client_key, client_secret, REDIRECT_URI)
    
    if token_info:
        print("\n✅ セットアップ完了！")
        print("\n次のステップ:")
        print("1. 上記のexportコマンドを実行")
        print("2. または .env ファイルに追加")
        print("3. upload_tiktok.py でテスト投稿")
    else:
        print("\n❌ セットアップ失敗")
        sys.exit(1)
