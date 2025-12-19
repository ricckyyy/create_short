# 📱 TikTok自動投稿セットアップガイド

## 🎯 概要

TikTok Content Posting APIを使用して、生成した動画を自動的にTikTokにアップロードする機能です。

## 🔑 準備：TikTok API セットアップ

### Step 1: TikTok Developer アカウント作成

1. **TikTok for Developers にアクセス**
   - URL: https://developers.tiktok.com/
   - 「Get Started」をクリック

2. **アカウント登録**
   - TikTokアカウントでログイン
   - 開発者利用規約に同意

### Step 2: アプリ作成

1. **「My Apps」→「Create New App」**

2. **アプリ情報を入力**
   ```
   App Name: Short Video Automation
   App Type: Web App
   Category: Content & Publishing
   ```

3. **必要な権限を選択**
   - `video.upload` - 動画アップロード
   - `video.publish` - 動画公開

### Step 3: アクセストークン取得

#### 方法A: OAuth 2.0（推奨）

```python
# 認証URLを生成
from upload_tiktok import TikTokUploader

CLIENT_KEY = "your_client_key"
CLIENT_SECRET = "your_client_secret"
REDIRECT_URI = "http://localhost:8000/callback"

# ユーザーをこのURLにリダイレクト
auth_url = f"https://www.tiktok.com/v2/auth/authorize/?client_key={CLIENT_KEY}&scope=video.upload,video.publish&response_type=code&redirect_uri={REDIRECT_URI}"
print(f"このURLを開いてください: {auth_url}")

# コールバックで取得したcodeを使ってアクセストークンを取得
code = input("取得したcodeを入力: ")

import requests
token_response = requests.post(
    "https://open.tiktokapis.com/v2/oauth/token/",
    data={
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
)

access_token = token_response.json()["access_token"]
print(f"アクセストークン: {access_token}")
```

#### 方法B: 環境変数設定

```bash
export TIKTOK_ACCESS_TOKEN="your_access_token_here"
```

## 📤 使い方

### 基本的な使い方

```python
from upload_tiktok import upload_to_tiktok

# 動画をアップロード
result = upload_to_tiktok(
    video_path="data/videos/draft/psychology_shinrigaku_20251113.mp4",
    account_name="心理テストラボ",
    script_text="あなたの性格を当てます...",
    access_token="your_access_token"
)

if result["success"]:
    print("✅ TikTok投稿完了！")
else:
    print(f"❌ エラー: {result['error']}")
```

### daily_generation.py に統合

```python
# daily_generation.py の最後に追加
import os
from upload_tiktok import upload_to_tiktok

TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")

if TIKTOK_ACCESS_TOKEN:
    # TikTokにもアップロード
    for acc in accounts_data:
        video_path = get_video_path(acc["name"], date_str, "draft")
        
        result = upload_to_tiktok(
            video_path=str(video_path),
            account_name=acc["name"],
            script_text=acc["script"],
            access_token=TIKTOK_ACCESS_TOKEN
        )
        
        if result["success"]:
            log_message(f"✅ {acc['name']} - TikTok投稿完了")
        else:
            log_message(f"❌ {acc['name']} - TikTok投稿失敗: {result['error']}")
```

## 🎨 カスタマイズ

### タイトル・説明文のカスタマイズ

`upload_tiktok.py` の `generate_tiktok_metadata()` 関数を編集：

```python
templates = {
    "心理テストラボ": {
        "title_prefix": "【心理テスト】",
        "description": "あなたのカスタム説明文\n\n#カスタムハッシュタグ",
        "hashtags": ["カスタム", "タグ", "リスト"]
    }
}
```

### 公開設定の変更

```python
uploader.upload_video(
    video_path=video_path,
    title=title,
    description=description,
    privacy_level="SELF_ONLY",  # 非公開（下書き）
    disable_comment=True,        # コメント無効
    disable_duet=True            # デュエット無効
)
```

## 🔒 セキュリティ

### アクセストークンの安全な保管

```bash
# .env ファイルを作成（.gitignoreに追加済み）
echo "TIKTOK_ACCESS_TOKEN=your_token_here" >> .env

# Python-dotenv で読み込み
pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os

load_dotenv()
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
```

## 📊 アップロード履歴

投稿履歴は自動的に保存されます：

```
data/upload/history/tiktok_20251113_060215.json
```

内容：
```json
{
  "platform": "TikTok",
  "video_path": "data/videos/draft/psychology_shinrigaku_20251113.mp4",
  "title": "【心理テスト】あなたの性格を当てます",
  "description": "結果はどうでしたか？...",
  "uploaded_at": "2025-11-13T06:02:15",
  "response": {...}
}
```

## 🐛 トラブルシューティング

### エラー: "Invalid access token"

**原因**: トークンが期限切れ

**解決策**:
```bash
# トークンを再取得
# OAuth フローを再実行
```

### エラー: "Video size exceeds limit"

**原因**: 動画サイズが大きすぎる（TikTokは最大287MB）

**解決策**:
```python
# 動画を圧縮
ffmpeg -i input.mp4 -b:v 2M -maxrate 2M -bufsize 1M output.mp4
```

### エラー: "Rate limit exceeded"

**原因**: API呼び出し回数制限

**解決策**:
- 投稿間隔を空ける（最低30秒）
- バッチ投稿の場合は時間を分散

## 📚 参考リンク

- **TikTok for Developers**: https://developers.tiktok.com/
- **Content Posting API ドキュメント**: https://developers.tiktok.com/doc/content-posting-api-get-started
- **API リファレンス**: https://developers.tiktok.com/doc/content-posting-api-reference

## 🎓 次のステップ

1. TikTok Developer アカウントを作成
2. アプリを登録してアクセストークンを取得
3. 環境変数を設定
4. テスト投稿を実行
5. daily_generation.py に統合

これで毎日自動的にTikTokに投稿されます！
