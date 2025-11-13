# TikTok自動投稿 - クイックスタートガイド

2つの実装方法から選べます。

## 🚀 方法1: Selenium版（推奨・5分で完了）

### セットアップ

```bash
# 1. 依存関係をインストール
pip install selenium webdriver-manager

# 2. テスト実行（ブラウザが開きます）
python -c "
from upload_tiktok_selenium import upload_to_tiktok_selenium
result = upload_to_tiktok_selenium(
    video_path='data/videos/draft/test.mp4',
    caption='テスト動画',
    hashtags=['心理テスト'],
    headless=False
)
print(result)
"

# 3. ブラウザでTikTokにログイン
# 4. ログイン完了後、Enterキーを押す
# 5. 動画が自動アップロードされます！
```

### 2回目以降は完全自動

```python
from upload_tiktok_selenium import upload_to_tiktok_selenium

# ヘッドレスモードで自動実行
result = upload_to_tiktok_selenium(
    video_path="data/videos/draft/shinrigaku.mp4",
    caption="【心理テスト】あなたの性格診断！",
    hashtags=["心理テスト", "診断", "性格"],
    headless=True  # ブラウザを表示しない
)
```

**メリット:**
- ✅ 5分でセットアップ完了
- ✅ TikTok開発者登録不要
- ✅ 一度ログインすれば自動化
- ✅ API制限なし

**デメリット:**
- ⚠️ TikTok UIが変わると修正必要
- ⚠️ やや遅い（20-30秒/動画）

---

## 🏢 方法2: 公式API版（長期運用向け）

### セットアップ（数時間〜数日）

```bash
# 1. TikTok開発者登録
# https://developers.tiktok.com/ でアカウント作成

# 2. アプリ作成・設定
# - プライバシーポリシー: https://github.com/ricckyyy/create_short/blob/develop/PRIVACY_POLICY.md
# - 利用規約: https://github.com/rickkyyy/create_short/blob/develop/TERMS_OF_SERVICE.md
# - Redirect URI: https://www.example.com/callback
# - Scopes: video.upload, video.publish

# 3. .env.tiktok を編集
# TIKTOK_CLIENT_KEY=あなたのClient Key
# TIKTOK_CLIENT_SECRET=あなたのClient Secret

# 4. OAuth認証
python scripts/tiktok_auth.py

# 5. ブラウザで認証 → トークン取得
```

### 使い方

```python
from upload_tiktok import upload_to_tiktok

result = upload_to_tiktok(
    video_path="data/videos/draft/shinrigaku.mp4",
    title="【心理テスト】あなたの性格は？",
    hashtags=["心理テスト", "診断"]
)
```

**メリット:**
- ✅ 公式サポート
- ✅ 高速（5-10秒/動画）
- ✅ 安定性が高い

**デメリット:**
- ❌ セットアップが複雑
- ❌ OAuth認証が必要
- ❌ API制限あり

---

## 📊 どっちを選ぶ？

| 用途 | 推奨 |
|------|------|
| **今すぐ試したい** | ✅ Selenium版 |
| **個人・小規模（1日数本）** | ✅ Selenium版 |
| **複数アカウント管理** | ✅ Selenium版 |
| **長期運用（1年以上）** | ✅ 公式API版 |
| **大規模（1日10本以上）** | ✅ 公式API版 |
| **ビジネス利用** | ✅ 公式API版 |

---

## 📚 詳細ドキュメント

- **Selenium版**: [docs/TIKTOK_SELENIUM_SETUP.md](docs/TIKTOK_SELENIUM_SETUP.md)
- **公式API版**: [docs/TIKTOK_SETUP.md](docs/TIKTOK_SETUP.md)
- **比較表**: [docs/TIKTOK_COMPARISON.md](docs/TIKTOK_COMPARISON.md)

---

## 🆘 トラブルシューティング

### Selenium版

**問題: ChromeDriverのバージョンエラー**
```bash
pip install webdriver-manager  # 自動で最適なバージョンをインストール
```

**問題: ログインが保持されない**
```bash
rm -rf ~/.chrome_tiktok_profile/  # プロファイルを削除して再ログイン
```

### 公式API版

**問題: OAuth認証エラー**
- TikTok Developer Portalで設定を確認
- Redirect URIが正しいか確認

**問題: トークンの有効期限切れ**
```bash
python scripts/tiktok_auth.py  # 再認証
```

---

## 🎬 daily_generation.pyへの統合

### Selenium版を使う場合

```python
# daily_generation.py の最後に追加

from upload_tiktok_selenium import upload_to_tiktok_selenium

# 動画生成後、TikTokに投稿
for video in generated_videos:
    upload_to_tiktok_selenium(
        video_path=video['path'],
        caption=video['caption'],
        hashtags=video['hashtags'],
        headless=True
    )
```

### 公式API版を使う場合

```python
# daily_generation.py の最後に追加

from upload_tiktok import upload_to_tiktok

# 動画生成後、TikTokに投稿
for video in generated_videos:
    upload_to_tiktok(
        video_path=video['path'],
        title=video['title'],
        hashtags=video['hashtags']
    )
```

---

**作成日**: 2025-01-12  
**ブランチ**: `feature/tiktok-selenium`  
**推奨**: まずSelenium版で試してみてください！
