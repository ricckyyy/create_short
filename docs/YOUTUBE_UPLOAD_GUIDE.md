# YouTube 自動投稿機能 - 使い方ガイド

## 🚀 セットアップ手順

### 1. YouTube API の設定
詳しくは [`docs/YOUTUBE_API_SETUP.md`](./YOUTUBE_API_SETUP.md) を参照してください。

**概要:**
1. Google Cloud Console でプロジェクト作成
2. YouTube Data API v3 を有効化
3. OAuth 2.0 クライアント ID 作成
4. `client_secrets.json` をダウンロード
5. プロジェクトルートに配置

### 2. 初回認証

```bash
# テストアップロードで認証
./scripts/test_youtube_upload.sh
```

ブラウザが開いて認証画面が表示されます:
1. Google アカウントでログイン
2. アクセス許可を承認
3. `token.pickle` が自動生成されます

## 📖 使い方

### 手動アップロード

#### 単体テスト
```bash
./scripts/test_youtube_upload.sh
```

#### Python から直接呼び出し
```python
from upload_youtube import upload_video, generate_metadata

# メタデータ生成
metadata = generate_metadata("心理テストラボ", "台本テキスト")

# アップロード
result = upload_video(
    video_path="data/videos/draft/shinrigaku.mp4",
    title=metadata["title"],
    description=metadata["description"],
    tags=metadata["tags"],
    privacy_status="public"  # public / unlisted / private
)

print(f"アップロード完了: {result['url']}")
```

### 自動アップロード（毎日実行）

**日次バッチ処理に組み込み済み:**

```bash
# 手動実行
./scripts/run_daily.sh

# cron 設定（毎日自動実行）
./scripts/setup_cron.sh
```

**処理フロー:**
1. AI 台本生成
2. 動画生成
3. **YouTube 自動アップロード** ← 追加！
4. ログ保存

## 🎯 メタデータテンプレート

各アカウント専用のテンプレートが自動適用されます:

### 心理テストラボ
```
タイトル: 【心理テスト】[台本の最初の行]
タグ: 心理テスト, 性格診断, 心理学, ...
説明文: 心理テストラボ用のテンプレート
```

### 闇夜の語り部
```
タイトル: 【怖い話】[台本の最初の行]
タグ: 怖い話, 都市伝説, ホラー, ...
説明文: 闇夜の語り部用のテンプレート
```

### 映画紹介
```
タイトル: 【映画紹介】[台本の最初の行]
タグ: 映画紹介, 映画レビュー, 映画, ...
説明文: 映画紹介用のテンプレート
```

## ⚙️ カスタマイズ

### メタデータのカスタマイズ

`upload_youtube.py` の `generate_metadata()` 関数を編集:

```python
templates = {
    "新しいアカウント": {
        "title_prefix": "【タイトル接頭辞】",
        "description": "説明文テンプレート",
        "tags": ["タグ1", "タグ2", ...]
    }
}
```

### 公開設定の変更

`daily_generation.py` の Line 97:

```python
privacy_status="public"  # public / unlisted / private
```

- `public`: 一般公開
- `unlisted`: 限定公開（URLを知っている人のみ）
- `private`: 非公開

## 📊 API クォータ制限

**YouTube Data API 制限:**
- 1日あたり 10,000 ユニット
- 動画アップロード 1本 = 約 1,600 ユニット
- **1日最大 6本** までアップロード可能

**現在の構成:**
- アカウント数: 3つ
- 1日1回実行 → **3本/日** (余裕あり)

## 🔧 トラブルシューティング

### エラー: "client_secrets.json が見つかりません"
```bash
# 解決方法
# 1. docs/YOUTUBE_API_SETUP.md を参照
# 2. client_secrets.json をプロジェクトルートに配置
ls -la client_secrets.json  # 確認
```

### エラー: "quotaExceeded"
```
⚠️ API クォータを超過しています
```

**対処法:**
- 翌日まで待つ（太平洋時間 午前0時にリセット）
- 不要なアップロードを減らす

### 認証のリセット
```bash
# token.pickle を削除して再認証
rm token.pickle
./scripts/test_youtube_upload.sh
```

### アップロード失敗時の動画確認
```bash
# 動画は生成済みなので手動でアップロード可能
ls data/videos/draft/
```

## 📁 関連ファイル

```
/home/rt/create_short/
├── upload_youtube.py              # YouTube アップロードスクリプト
├── client_secrets.json            # YouTube API 認証情報（要配置）
├── token.pickle                   # 認証トークン（自動生成）
├── daily_generation.py            # 自動投稿統合済み
├── scripts/
│   └── test_youtube_upload.sh    # テストスクリプト
└── docs/
    ├── YOUTUBE_API_SETUP.md       # API 設定ガイド
    └── YOUTUBE_UPLOAD_GUIDE.md    # このファイル
```

## 🎥 アップロード後の確認

### YouTube Studio で確認
https://studio.youtube.com

1. 「コンテンツ」タブ
2. アップロードした動画を確認
3. サムネイル設定、説明文編集など

### ログで確認
```bash
# 最新のログを確認
cat data/logs/generation/generation_$(date +%Y%m%d).log
```

## ⚡ ベストプラクティス

1. **テスト時は `unlisted` で**: 公開前に確認
2. **クォータ監視**: 毎日のログでエラーチェック
3. **バックアップ**: 動画ファイルは自動保存されます
4. **定期確認**: YouTube Studio で視聴データ分析

## 📚 参考リンク
- [YouTube Data API v3 公式ドキュメント](https://developers.google.com/youtube/v3)
- [OAuth 2.0 認証ガイド](https://developers.google.com/identity/protocols/oauth2)
- [API クォータ計算ツール](https://developers.google.com/youtube/v3/determine_quota_cost)
