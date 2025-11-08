# Git ワークフローガイド

## 📋 ブランチ戦略（GitHub Flow）

このプロジェクトでは **GitHub Flow** を採用します。シンプルで小規模チームに最適です。

### ブランチ構成

```
main (保護ブランチ)
  ├── develop (開発用メインブランチ)
  │   ├── feature/youtube-upload (機能開発)
  │   ├── feature/ai-script-generation (機能開発)
  │   ├── fix/voice-generation-bug (バグ修正)
  │   └── hotfix/critical-error (緊急修正)
  └── release/v1.0.0 (リリース準備)
```

## 🌿 ブランチの種類

### 1. `main` ブランチ
- **用途**: 本番環境で動作するコード
- **保護**: 直接 push 禁止、Pull Request 経由のみ
- **デプロイ**: このブランチから自動デプロイ

### 2. `develop` ブランチ
- **用途**: 開発中の最新コード
- **マージ元**: feature, fix ブランチ
- **マージ先**: main ブランチ（リリース時）

### 3. `feature/*` ブランチ
- **用途**: 新機能開発
- **命名**: `feature/機能名`
- **例**: `feature/tiktok-upload`, `feature/thumbnail-generator`

### 4. `fix/*` ブランチ
- **用途**: バグ修正
- **命名**: `fix/バグ内容`
- **例**: `fix/video-encoding-error`

### 5. `hotfix/*` ブランチ
- **用途**: 本番環境の緊急修正
- **命名**: `hotfix/問題内容`
- **分岐元**: `main`
- **マージ先**: `main` と `develop` 両方

## 🔄 作業フロー

### 新機能開発の流れ

```bash
# 1. develop ブランチを最新化
git checkout develop
git pull origin develop

# 2. 機能ブランチを作成
git checkout -b feature/youtube-upload

# 3. 作業・コミット
git add .
git commit -m "feat: YouTube自動アップロード機能を実装"

# 4. リモートにプッシュ
git push origin feature/youtube-upload

# 5. GitHub で Pull Request 作成
# develop ← feature/youtube-upload

# 6. レビュー・マージ後、ブランチ削除
git checkout develop
git pull origin develop
git branch -d feature/youtube-upload
```

### バグ修正の流れ

```bash
# 1. fix ブランチを作成
git checkout develop
git checkout -b fix/voice-generation-bug

# 2. 修正・テスト
# ...コード修正...

# 3. コミット
git add .
git commit -m "fix: VOICEVOX接続エラーを修正"

# 4. プッシュ・PR
git push origin fix/voice-generation-bug
```

### 緊急修正（Hotfix）の流れ

```bash
# 1. main から hotfix ブランチ作成
git checkout main
git pull origin main
git checkout -b hotfix/critical-api-error

# 2. 修正
# ...緊急修正...

# 3. コミット
git commit -am "hotfix: API認証エラーの緊急修正"

# 4. main にマージ
git checkout main
git merge hotfix/critical-api-error
git push origin main

# 5. develop にもマージ
git checkout develop
git merge hotfix/critical-api-error
git push origin develop

# 6. ブランチ削除
git branch -d hotfix/critical-api-error
```

## 📝 コミットメッセージ規約（Conventional Commits）

### フォーマット
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type（必須）
- **feat**: 新機能追加
- **fix**: バグ修正
- **docs**: ドキュメント変更
- **style**: コードスタイル修正（動作に影響なし）
- **refactor**: リファクタリング
- **perf**: パフォーマンス改善
- **test**: テスト追加・修正
- **chore**: ビルドプロセスや補助ツールの変更

### 例

```bash
# 新機能
git commit -m "feat(upload): YouTube自動アップロード機能を追加"

# バグ修正
git commit -m "fix(voice): VOICEVOX接続エラーを修正"

# ドキュメント
git commit -m "docs(readme): セットアップ手順を更新"

# リファクタリング
git commit -m "refactor(config): パス管理を一元化"

# 複数行の詳細説明
git commit -m "feat(ai): AI台本生成機能を実装

- OpenAI GPT-4対応
- Claude API対応
- フォールバックテンプレート機能

Closes #123"
```

## 🏷️ タグ付け（バージョン管理）

### セマンティックバージョニング（SemVer）

```
v{MAJOR}.{MINOR}.{PATCH}
```

- **MAJOR**: 互換性のない変更
- **MINOR**: 後方互換性のある機能追加
- **PATCH**: 後方互換性のあるバグ修正

### リリース手順

```bash
# 1. develop を main にマージ
git checkout main
git merge develop

# 2. バージョンタグを付与
git tag -a v1.0.0 -m "Release v1.0.0

- YouTube自動投稿機能
- AI台本生成機能
- Webアプリケーション"

# 3. タグをプッシュ
git push origin main
git push origin v1.0.0

# 4. GitHub で Release を作成
```

## 🛡️ ブランチ保護ルール（GitHub設定推奨）

### main ブランチ保護
1. GitHub リポジトリ → Settings → Branches
2. "Add branch protection rule"
3. 設定:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators

## 📊 .gitignore ベストプラクティス

既に設定済み（確認用）:

```bash
cat .gitignore
```

重要な除外項目:
- 認証情報: `client_secrets.json`, `token.pickle`
- APIキー: `.env`
- 動画ファイル: `*.mp4`
- 一時ファイル: `clip*.mp4`

## 🔍 よく使うコマンド

```bash
# ブランチ一覧
git branch -a

# 現在のブランチ確認
git branch --show-current

# リモートブランチと同期
git fetch origin

# ブランチ削除（ローカル）
git branch -d feature/old-feature

# ブランチ削除（リモート）
git push origin --delete feature/old-feature

# コミット履歴を綺麗に表示
git log --oneline --graph --all

# 変更差分確認
git diff develop main

# 特定ファイルの履歴
git log --follow -- upload_youtube.py
```

## 🚀 Pull Request テンプレート

以下を `.github/pull_request_template.md` に保存:

```markdown
## 📝 変更内容

<!-- 何を変更したか簡潔に説明 -->

## 🎯 目的

<!-- なぜこの変更が必要か -->

## ✅ チェックリスト

- [ ] テスト済み
- [ ] ドキュメント更新済み
- [ ] コミットメッセージが規約に従っている
- [ ] ブランチ名が規約に従っている

## 📸 スクリーンショット

<!-- UI変更がある場合 -->

## 🔗 関連Issue

Closes #
```

## 📚 参考リンク

- [GitHub Flow](https://docs.github.com/ja/get-started/quickstart/github-flow)
- [Conventional Commits](https://www.conventionalcommits.org/ja/)
- [Semantic Versioning](https://semver.org/lang/ja/)
