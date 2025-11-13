# TikTok自動投稿セットアップガイド（Selenium版）

公式APIより**圧倒的に簡単**なSelenium版の設定手順です。

## 🎯 この方法のメリット

### ✅ Selenium版（この方法）
- ✅ **TikTok開発者アカウント不要**
- ✅ **OAuth認証不要**
- ✅ **アプリ審査不要**
- ✅ **API制限なし**
- ✅ 一度ログインすれば自動化可能
- ✅ 実際のブラウザを使うので確実

### ❌ 公式API版（複雑）
- ❌ TikTok開発者登録が必要
- ❌ OAuth 2.0 + PKCE認証
- ❌ 審査・検証プロセス
- ❌ API使用制限あり
- ❌ プライバシーポリシー・利用規約が必要

---

## 📦 必要なもの

### 1. Google Chrome
すでにインストール済みならOK。

### 2. ChromeDriver
Chromeのバージョンに合わせてインストール。

### 3. Selenium
```bash
pip install selenium
```

---

## 🚀 セットアップ手順

### Step 1: ChromeDriverのインストール

#### 方法A: 自動インストール（推奨）
```bash
pip install webdriver-manager
```

`upload_tiktok_selenium.py`の以下の行を変更：
```python
# 変更前
self.driver = webdriver.Chrome(options=options)

# 変更後
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())
self.driver = webdriver.Chrome(service=service, options=options)
```

#### 方法B: 手動インストール
1. Chromeのバージョンを確認：
   ```bash
   google-chrome --version
   ```

2. [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)から対応バージョンをダウンロード

3. PATHに追加：
   ```bash
   # Linux/Mac
   sudo mv chromedriver /usr/local/bin/
   sudo chmod +x /usr/local/bin/chromedriver
   
   # Windows
   # chromedriver.exeをC:\Windows\にコピー
   ```

### Step 2: 初回ログイン

初回実行時、ブラウザが開いてTikTokのログイン画面が表示されます：

```python
from upload_tiktok_selenium import upload_to_tiktok_selenium

# 初回実行（headless=False でブラウザを表示）
result = upload_to_tiktok_selenium(
    video_path="data/videos/draft/test.mp4",
    caption="テスト動画",
    hashtags=["心理テスト"],
    headless=False  # ブラウザを表示
)
```

**手動で以下を実行：**
1. ブラウザが開く
2. TikTokにログイン（メール/電話番号/SNS連携）
3. ログイン完了後、ターミナルで**Enter**を押す
4. 動画がアップロードされる

### Step 3: ログイン情報を保存

ログインすると、Chromeのユーザープロファイルに保存されます：
- 保存場所: `~/.chrome_tiktok_profile/`
- 次回以降は自動ログイン

### Step 4: 自動化

2回目以降は完全自動：

```python
from upload_tiktok_selenium import upload_to_tiktok_selenium

# ヘッドレスモードで自動実行
result = upload_to_tiktok_selenium(
    video_path="data/videos/draft/shinrigaku.mp4",
    caption="【心理テスト】あなたの性格診断！",
    hashtags=["心理テスト", "診断", "性格"],
    headless=True  # ブラウザを表示しない
)

print(result)
# {'success': True, 'video_path': '...', 'caption': '...'}
```

---

## 🔧 使い方

### 基本的な使い方

```python
from upload_tiktok_selenium import TikTokSeleniumUploader

uploader = TikTokSeleniumUploader(headless=False)

result = uploader.upload_video(
    video_path="data/videos/draft/movie.mp4",
    caption="映画紹介です！",
    hashtags=["映画", "レビュー", "おすすめ"],
    privacy="public",  # "public", "friends", "private"
    allow_comments=True,
    allow_duet=True,
    allow_stitch=True
)

print(f"アップロード成功: {result['success']}")
```

### daily_generation.pyに統合

```python
# daily_generation.py の最後に追加

from upload_tiktok_selenium import upload_to_tiktok_selenium

def upload_videos_to_tiktok():
    """生成した動画をTikTokに投稿"""
    import sqlite3
    from datetime import datetime
    
    # 今日の動画を取得
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y%m%d")
    cursor.execute("""
        SELECT account_name, file_path, title, hashtags 
        FROM videos 
        WHERE created_at LIKE ? 
        AND uploaded_to_tiktok = 0
    """, (f"{today}%",))
    
    videos = cursor.fetchall()
    
    for account_name, file_path, title, hashtags_str in videos:
        print(f"\n📤 TikTokアップロード: {account_name}")
        
        # ハッシュタグをリストに変換
        hashtags = hashtags_str.split() if hashtags_str else []
        
        # アップロード
        result = upload_to_tiktok_selenium(
            video_path=file_path,
            caption=title,
            hashtags=hashtags,
            headless=True
        )
        
        if result['success']:
            # データベースを更新
            cursor.execute("""
                UPDATE videos 
                SET uploaded_to_tiktok = 1,
                    tiktok_uploaded_at = ?
                WHERE file_path = ?
            """, (datetime.now(), file_path))
            conn.commit()
            print(f"✅ {account_name} 投稿完了")
        else:
            print(f"❌ {account_name} 投稿失敗: {result.get('error')}")
    
    conn.close()

# 動画生成後に実行
if __name__ == "__main__":
    generate_all_videos()
    upload_videos_to_tiktok()  # TikTokに自動投稿
```

---

## 🐛 トラブルシューティング

### 問題1: ChromeDriverのバージョンエラー

```
SessionNotCreatedException: session not created: This version of ChromeDriver only supports Chrome version XX
```

**解決策:**
- Chromeを最新版に更新
- または、ChromeDriverのバージョンをChromeに合わせる

### 問題2: ログイン画面が表示されない

```bash
# ユーザープロファイルを削除してやり直し
rm -rf ~/.chrome_tiktok_profile/
```

### 問題3: 要素が見つからない

TikTokのUIが変更された可能性があります。

**デバッグ方法:**
```python
# headless=False でブラウザを表示して確認
uploader = TikTokSeleniumUploader(headless=False)
```

ブラウザで実際の動作を見て、`upload_tiktok_selenium.py`のセレクタを修正：

```python
# 例: キャプション入力欄のセレクタが変わった場合
caption_box = self.wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "新しいセレクタ"))
)
```

### 問題4: アップロードが途中で止まる

タイムアウト時間を延長：

```python
# upload_tiktok_selenium.py の WebDriverWait を変更
self.wait = WebDriverWait(self.driver, 60)  # 30秒 → 60秒
```

### 問題5: 複数アカウントで使いたい

アカウントごとにプロファイルを分ける：

```python
# アカウントAのプロファイル
uploader_a = TikTokSeleniumUploader(user_data_dir="~/.chrome_tiktok_account_a")

# アカウントBのプロファイル
uploader_b = TikTokSeleniumUploader(user_data_dir="~/.chrome_tiktok_account_b")
```

初回はそれぞれログインが必要です。

---

## 📊 公式API版との比較

| 項目 | Selenium版 | 公式API版 |
|------|-----------|----------|
| **セットアップ** | ✅ 5分 | ❌ 数時間〜数日 |
| **開発者登録** | ✅ 不要 | ❌ 必要 |
| **認証** | ✅ 一度ログインするだけ | ❌ OAuth 2.0 + PKCE |
| **審査** | ✅ 不要 | ❌ 必要 |
| **API制限** | ✅ なし | ❌ あり |
| **安定性** | ⚠️ UIが変わると修正必要 | ✅ 安定 |
| **スピード** | ⚠️ やや遅い（ブラウザ起動） | ✅ 高速 |
| **複数アカウント** | ✅ 簡単 | ⚠️ アプリごとに設定 |

---

## 🎬 動作の流れ

1. **ChromeDriver起動** - ユーザープロファイルを読み込み
2. **TikTok Studioにアクセス** - https://www.tiktok.com/creator-center/upload
3. **ログイン確認** - 初回はログイン待機、2回目以降は自動
4. **ファイルアップロード** - `<input type="file">`に動画パスを送信
5. **キャプション入力** - テキストエリアに説明文+ハッシュタグ
6. **公開設定** - 公開/友達/非公開を選択
7. **投稿ボタンクリック** - 投稿実行
8. **完了確認** - "投稿しました"メッセージを待つ
9. **履歴保存** - `data/upload/tiktok_selenium_*.json`に記録

---

## 💡 Tips

### ヘッドレスモードでの実行

サーバーで実行する場合：

```bash
# Xvfb（仮想ディスプレイ）をインストール
sudo apt-get install xvfb

# Xvfb経由で実行
xvfb-run python daily_generation.py
```

### ログの確認

```python
# 詳細ログを有効化
import logging
logging.basicConfig(level=logging.DEBUG)
```

### スクリーンショットを保存

デバッグ用：

```python
# upload_tiktok_selenium.py に追加
self.driver.save_screenshot("debug_screenshot.png")
```

---

## 🔒 セキュリティ

- **ログイン情報**: `~/.chrome_tiktok_profile/`に保存されるため、このディレクトリを保護してください
- **サーバー実行**: 本番環境では専用ユーザーで実行
- **アクセス制限**: プロファイルディレクトリのパーミッションを制限

```bash
chmod 700 ~/.chrome_tiktok_profile/
```

---

## 📝 まとめ

Selenium版は**公式APIより圧倒的に簡単**です：

1. **5分でセットアップ完了**
2. **一度ログインすれば完全自動**
3. **TikTok開発者登録不要**
4. **審査・制限なし**

ただし、TikTokのUIが変更された場合は、セレクタの修正が必要になる可能性があります。

**長期的な安定性を求めるなら公式API、簡単さを求めるならSelenium**という選択になります。

---

## 🔗 参考リンク

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
- [TikTok Creator Portal](https://www.tiktok.com/creator-center/upload)

---

**作成日**: 2025-01-12  
**対象**: TikTok自動投稿（Selenium版）
