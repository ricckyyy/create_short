# YouTube API 設定ガイド

## 📋 概要
YouTube Shorts への自動投稿には YouTube Data API v3 を使用します。

## 🔧 1. Google Cloud Console での設定

### 1.1 プロジェクト作成
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成（例: "create-short-uploader"）

### 1.2 YouTube Data API v3 を有効化
1. 「APIとサービス」→「ライブラリ」
2. "YouTube Data API v3" を検索
3. 「有効にする」をクリック

### 1.3 OAuth 2.0 認証情報の作成
1. 「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「OAuth クライアント ID」
3. アプリケーションの種類: **デスクトップアプリ**
4. 名前: "YouTube Uploader"
5. 「作成」をクリック

### 1.4 client_secrets.json のダウンロード
1. 作成した OAuth クライアント ID の右側の「⬇」アイコンをクリック
2. JSON ファイルをダウンロード
3. ファイル名を `client_secrets.json` に変更
4. プロジェクトルート (`/home/rt/create_short/`) に配置

```bash
# 配置例
/home/rt/create_short/
├── client_secrets.json  ← ここに配置
├── config.py
├── upload_youtube.py
...
```

## 🔐 2. OAuth 同意画面の設定（重要！）

### 2.1 同意画面の構成
1. 「APIとサービス」→「OAuth 同意画面」
2. ユーザータイプ: **外部** を選択
3. アプリ名、サポートメール、デベロッパー連絡先を入力
4. スコープの追加:
   - `https://www.googleapis.com/auth/youtube.upload`
   - `https://www.googleapis.com/auth/youtube`

### 2.2 テストユーザーの追加
1. 「テストユーザー」セクションで「ユーザーを追加」
2. YouTube にアップロードする Google アカウントのメールアドレスを追加

## ✅ 3. 初回認証

初回実行時、ブラウザが開いて認証を求められます:

```bash
./scripts/test_youtube_upload.sh
```

1. Google アカウントでログイン
2. 「このアプリは確認されていません」→「詳細」→「(アプリ名)に移動」
3. アクセス許可を承認
4. 認証完了後、`token.pickle` が自動生成されます

## 📁 生成されるファイル

```
/home/rt/create_short/
├── client_secrets.json  # あなたがダウンロードしたファイル
└── token.pickle         # 初回認証後に自動生成（再認証不要）
```

## 🚨 注意事項

### セキュリティ
- `client_secrets.json` と `token.pickle` は **Git にコミットしない**
- `.gitignore` に追加済み

### API クォータ
- YouTube Data API には 1 日あたり 10,000 ユニットの制限があります
- 動画アップロード: 約 1,600 ユニット/本
- **1日6本まで** アップロード可能

### 公開設定
- 初期設定は `unlisted`（限定公開）
- 本番運用時は `public` に変更

## 🔄 トラブルシューティング

### "access_denied" エラー
- OAuth 同意画面でテストユーザーに追加されているか確認
- スコープに `youtube.upload` が含まれているか確認

### "quotaExceeded" エラー
- 翌日まで待つ（太平洋時間の午前0時にリセット）

### 認証のリセット
```bash
rm token.pickle
# 次回実行時に再認証
```

## 📚 参考リンク
- [YouTube Data API - 公式ドキュメント](https://developers.google.com/youtube/v3)
- [OAuth 2.0 認証](https://developers.google.com/identity/protocols/oauth2)
- [API クォータの詳細](https://developers.google.com/youtube/v3/getting-started#quota)
