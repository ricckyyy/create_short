# TikTok自動投稿: 公式API vs Selenium 比較ガイド

このプロジェクトには**2つのTikTok投稿方法**が実装されています。

---

## 📊 比較表

| 項目 | Selenium版 | 公式API版 |
|------|-----------|----------|
| **実装ファイル** | `upload_tiktok_selenium.py` | `upload_tiktok.py` |
| **セットアップガイド** | `docs/TIKTOK_SELENIUM_SETUP.md` | `docs/TIKTOK_SETUP.md` |
| **セットアップ時間** | ✅ **5分** | ❌ 数時間〜数日 |
| **TikTok開発者登録** | ✅ **不要** | ❌ 必要 |
| **OAuth認証** | ✅ **不要** | ❌ OAuth 2.0 + PKCE |
| **アプリ審査** | ✅ **不要** | ❌ 必要 |
| **プライバシーポリシー** | ✅ **不要** | ❌ 必須 |
| **API使用制限** | ✅ **なし** | ❌ あり（レート制限） |
| **複数アカウント** | ✅ **簡単**（プロファイル分け） | ⚠️ アプリごとに設定 |
| **実行スピード** | ⚠️ やや遅い（20-30秒/動画） | ✅ 高速（5-10秒/動画） |
| **安定性** | ⚠️ UIが変わると修正必要 | ✅ **安定**（公式サポート） |
| **サーバー実行** | ⚠️ Xvfbが必要（仮想ディスプレイ） | ✅ **簡単**（API呼び出しのみ） |
| **依存関係** | Selenium + ChromeDriver + Chrome | ✅ requests のみ |
| **メンテナンス** | ⚠️ TikTok UI変更で要修正 | ✅ **不要**（API安定） |
| **エラーハンドリング** | ⚠️ 複雑（要素が見つからない等） | ✅ **シンプル**（HTTPステータス） |
| **デバッグ** | ⚠️ 難しい（ブラウザ動作確認） | ✅ **簡単**（ログ確認） |

---

## 🎯 推奨される使い方

### ✅ Selenium版を選ぶべき場合

1. **今すぐ使いたい**
   - セットアップに時間をかけたくない
   - TikTok開発者登録が面倒

2. **個人利用・小規模**
   - 1日数本程度の投稿
   - テスト・実験目的

3. **複数アカウント管理**
   - 3つのアカウントを簡単に切り替えたい
   - プロファイルを分ければOK

4. **API制限を避けたい**
   - レート制限なしで自由に投稿

### ✅ 公式API版を選ぶべき場合

1. **長期運用**
   - 1年以上の継続利用
   - 安定性・メンテナンス性重視

2. **大規模・自動化**
   - 1日10本以上の投稿
   - サーバーで完全自動化

3. **ビジネス利用**
   - 公式サポートが欲しい
   - 規約違反リスクを避けたい

4. **高速処理**
   - 大量の動画を高速アップロード
   - ブラウザ起動のオーバーヘッドを避けたい

---

## 🚀 実装の使い分け

### パターン1: まずはSeleniumで試す（推奨）

```python
# Step 1: Selenium版でテスト（5分でセットアップ）
from upload_tiktok_selenium import upload_to_tiktok_selenium

result = upload_to_tiktok_selenium(
    video_path="data/videos/draft/test.mp4",
    caption="テスト動画",
    hashtags=["心理テスト"],
    headless=False
)

# Step 2: うまく動いたら自動化
# daily_generation.py に統合
```

### パターン2: 安定運用が必要なら公式API

```python
# Step 1: TikTok開発者登録（数時間〜数日）
# - https://developers.tiktok.com/ で登録
# - プライバシーポリシー・利用規約を作成
# - アプリ作成・設定

# Step 2: OAuth認証（初回のみ）
python scripts/tiktok_auth.py

# Step 3: 自動投稿
from upload_tiktok import upload_to_tiktok

result = upload_to_tiktok(
    video_path="data/videos/draft/test.mp4",
    caption="テスト動画",
    hashtags=["心理テスト"]
)
```

### パターン3: 併用（ハイブリッド）

```python
# 公式APIをメインにして、エラー時はSeleniumにフォールバック

def upload_with_fallback(video_path, caption, hashtags):
    """公式API → Selenium の順で試す"""
    
    # まず公式APIで試す
    try:
        from upload_tiktok import upload_to_tiktok
        result = upload_to_tiktok(video_path, caption, hashtags)
        if result['success']:
            return result
    except Exception as e:
        print(f"公式API失敗: {e}")
    
    # 失敗したらSeleniumにフォールバック
    from upload_tiktok_selenium import upload_to_tiktok_selenium
    return upload_to_tiktok_selenium(video_path, caption, hashtags)
```

---

## 📁 ファイル構成

```
create_short/
├── upload_tiktok.py              # 公式API版
├── upload_tiktok_selenium.py     # Selenium版
├── scripts/
│   └── tiktok_auth.py            # 公式API用OAuth認証
├── docs/
│   ├── TIKTOK_SETUP.md           # 公式API版セットアップガイド
│   ├── TIKTOK_SELENIUM_SETUP.md  # Selenium版セットアップガイド
│   └── TIKTOK_COMPARISON.md      # このファイル
├── PRIVACY_POLICY.md             # 公式API用（必須）
├── TERMS_OF_SERVICE.md           # 公式API用（必須）
└── .env.tiktok                   # 公式API用認証情報
```

---

## 🔧 セットアップ手順の違い

### Selenium版（5分）

```bash
# 1. Seleniumインストール
pip install selenium

# 2. ChromeDriverインストール
pip install webdriver-manager

# 3. 初回実行（ログイン）
python -c "from upload_tiktok_selenium import upload_to_tiktok_selenium; \
upload_to_tiktok_selenium('data/videos/draft/test.mp4', 'テスト', headless=False)"

# ブラウザでTikTokにログイン → 完了
```

### 公式API版（数時間〜数日）

```bash
# 1. TikTok開発者登録
# https://developers.tiktok.com/ でアカウント作成

# 2. アプリ作成
# - プライバシーポリシー・利用規約を用意
# - Redirect URI設定
# - Scopes設定（video.upload, video.publish）

# 3. OAuth認証
python scripts/tiktok_auth.py
# ブラウザで認証 → トークン取得

# 4. トークン設定
# .env.tiktokにアクセストークンを保存

# 完了（長い...）
```

---

## 💻 コード例

### Selenium版

```python
from upload_tiktok_selenium import upload_to_tiktok_selenium

# シンプル！
result = upload_to_tiktok_selenium(
    video_path="data/videos/draft/shinrigaku.mp4",
    caption="【心理テスト】あなたの性格は？",
    hashtags=["心理テスト", "診断"],
    headless=True  # 自動実行
)

print(result)
# {'success': True, 'video_path': '...', 'caption': '...'}
```

### 公式API版

```python
from upload_tiktok import upload_to_tiktok

# 事前にOAuth認証が必要
result = upload_to_tiktok(
    video_path="data/videos/draft/shinrigaku.mp4",
    title="【心理テスト】あなたの性格は？",
    hashtags=["心理テスト", "診断"]
)

print(result)
# {'success': True, 'share_id': 'v_xxx', 'video_id': 'xxx'}
```

---

## 🐛 トラブルシューティング

### Selenium版でよくある問題

1. **ChromeDriverのバージョンエラー**
   - 解決: `pip install webdriver-manager` で自動管理

2. **要素が見つからない**
   - 原因: TikTokのUIが変更された
   - 解決: セレクタを修正（`upload_tiktok_selenium.py`）

3. **ログインが必要と表示される**
   - 解決: `rm -rf ~/.chrome_tiktok_profile/` で再ログイン

### 公式API版でよくある問題

1. **OAuth認証エラー**
   - 原因: Redirect URIの設定ミス
   - 解決: `TIKTOK_SETUP.md`を確認

2. **アップロードエラー**
   - 原因: トークンの有効期限切れ
   - 解決: `python scripts/tiktok_auth.py` で再認証

3. **Scopeエラー**
   - 原因: `video.upload`スコープがない
   - 解決: TikTok Developer Portalで設定

---

## 📝 まとめ

### このプロジェクトの推奨フロー

```
1. まずSelenium版で試す（5分）
   ↓
2. うまく動作したら自動化
   ↓
3. 長期運用するなら公式APIに移行
   （時間があれば）
```

### 最終的な選択

- **個人・小規模** → **Selenium版**で十分
- **ビジネス・大規模** → **公式API版**に移行

どちらも実装済みなので、**状況に応じて使い分け**できます！

---

## 🔗 関連ドキュメント

- [Selenium版セットアップガイド](./TIKTOK_SELENIUM_SETUP.md)
- [公式API版セットアップガイド](./TIKTOK_SETUP.md)
- [プライバシーポリシー](../PRIVACY_POLICY.md)（公式API用）
- [利用規約](../TERMS_OF_SERVICE.md)（公式API用）

---

**作成日**: 2025-01-12  
**ブランチ**: `feature/tiktok-selenium`
