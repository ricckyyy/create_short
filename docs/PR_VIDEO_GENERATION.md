# PR連動動画生成機能

## 概要

プルリクエストの作成・更新時に自動で動画を生成する機能を追加しました。

## 機能詳細

### 自動実行タイミング
- PRの作成時（`opened`）
- PRの更新時（`synchronize`）
- PRの再オープン時（`reopened`）

### 監視対象ファイル
以下のファイルが変更された場合にのみ実行：
- `daily_generation.py`
- `create_movie.py`
- `generate_script.py`
- `config.py`
- `.github/workflows/pr-video-generation.yml`

### 自動通知機能
生成完了後、以下の内容でPRにコメントを自動投稿：
- 生成された動画ファイルのリスト
- Artifactsのダウンロードリンク
- 生成日時（日本時間）

## ワークフローファイル

### 1. セルフホストランナー用（推奨）
**ファイル**: `.github/workflows/pr-video-generation.yml`

**特徴**:
- すぐに使用可能（デフォルトで有効）
- 高速実行（15-30分）
- 安定した動作

**要件**:
- セルフホストランナーが必要
- VOICEVOX（Docker）が必要
- Ollamaが必要

### 2. GitHub-hostedランナー用（実験的）
**ファイル**: `.github/workflows/pr-video-generation-cloud.yml`

**特徴**:
- デフォルトで無効（手動実行のみ）
- サーバー不要
- 初回は時間がかかる（30-60分）

**有効化方法**:
ファイル内の `pull_request` セクションのコメントを解除

## 使用方法

### セットアップ（初回のみ）
1. セルフホストランナーをセットアップ
   ```bash
   # GitHubリポジトリ → Settings → Actions → Runners
   # 表示される手順に従ってランナーをインストール
   ```

2. 必要なサービスを起動
   ```bash
   # Ollama
   ollama serve &
   
   # VOICEVOX
   docker run -d --name voicevox -p 50021:50021 \
     voicevox/voicevox_engine:cpu-ubuntu20.04-latest
   ```

3. ランナーをサービスとして起動
   ```bash
   sudo ./svc.sh install
   sudo ./svc.sh start
   ```

### 日常使用
1. **PRを作成**
   ```bash
   git checkout -b feature/my-changes
   git add .
   git commit -m "変更内容"
   git push origin feature/my-changes
   # GitHub UIでPRを作成
   ```

2. **自動実行を確認**
   - Actions タブで実行状況を確認
   - 完了まで待つ（15-30分）

3. **動画をダウンロード**
   - PRに投稿されたコメントのリンクをクリック
   - Artifactsから動画をダウンロード

## Artifactsの命名規則

### セルフホストランナー
```
generated-videos-pr-{PR番号}-{実行番号}
```
例: `generated-videos-pr-42-123`

### GitHub-hostedランナー
```
generated-videos-pr-cloud-{PR番号}-{実行番号}
```
例: `generated-videos-pr-cloud-42-123`

## 権限設定

ワークフローには以下の最小権限が設定されています：
```yaml
permissions:
  contents: read      # リポジトリのコード読み取り
  actions: write      # Artifactsアップロード
  pull-requests: write # PRコメント投稿
```

## トラブルシューティング

### ワークフローが実行されない
**原因**: 監視対象ファイルが変更されていない

**解決策**:
- 対象ファイル（`daily_generation.py`等）を変更
- または手動実行を使用

### サービスが起動しない
**原因**: セルフホストランナーでVOICEVOXまたはOllamaが起動していない

**解決策**:
```bash
# VOICEVOX
docker start voicevox
curl http://127.0.0.1:50021/speakers

# Ollama
ollama serve &
curl http://127.0.0.1:11434/api/tags
```

### PRコメントが投稿されない
**原因**: ワークフローの実行に失敗している

**解決策**:
- Actions タブで実行ログを確認
- エラーメッセージを確認して対処

## 無効化方法

PR連動実行を無効化する場合：

### 方法1: ファイルを削除
```bash
git rm .github/workflows/pr-video-generation.yml
git rm .github/workflows/pr-video-generation-cloud.yml
git commit -m "PR連動動画生成を無効化"
```

### 方法2: ファイル名を変更
```bash
mv .github/workflows/pr-video-generation.yml \
   .github/workflows/pr-video-generation.yml.disabled
```

## 利点

### 開発フロー統合
- コードレビューと動画確認を同時に実施
- 変更の影響を即座に確認可能

### 品質向上
- 各変更で動画を自動生成
- 問題の早期発見が可能

### 効率化
- 手動実行の手間を削減
- 自動通知で作業フロー改善

## 今後の拡張案

1. **複数アカウント選択**: PR説明文から生成するアカウントを選択
2. **並列実行**: 複数アカウントの動画を並列生成
3. **プレビュー機能**: 動画のサムネイルをPRコメントに表示
4. **品質チェック**: 生成された動画の品質を自動検証

## 関連ドキュメント

- [GitHub Actions セットアップガイド](GITHUB_ACTIONS_SETUP.md)
- [クイックスタートガイド](GITHUB_ACTIONS_QUICKSTART.md)
- [システム構成図](GITHUB_ACTIONS_ARCHITECTURE.md)

---

**作成日**: 2025-12-25
**機能追加コミット**: 186c6ba
