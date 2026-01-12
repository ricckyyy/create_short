# GitHub Actions 自動実行セットアップガイド

このガイドでは、GitHub Actionsを使用して毎日6:00 AMに自動で動画を生成する方法を説明します。

## 📋 概要

GitHub Actionsワークフロー `.github/workflows/daily-video-generation.yml` により、以下が自動実行されます：

- **実行スケジュール**: 毎日 UTC 21:00（日本時間 6:00 AM）
- **手動実行**: GitHub UIから手動でも実行可能
- **処理内容**: 
  1. 台本の自動生成
  2. 音声ファイルの生成
  3. 動画の作成
  4. メタデータ（タイトル・説明文）の生成

## 🔧 セットアップ方法

### 1. セルフホストランナーのセットアップ（推奨）

このプロジェクトは以下のサービスに依存するため、**セルフホストランナー**の使用を推奨します：

- **VOICEVOX Engine** (Docker)
- **Ollama** (ローカルLLM)
- 大容量ストレージ（動画ファイル保存用）

#### セルフホストランナーの設定手順

1. **GitHubリポジトリ設定へ移動**
   ```
   リポジトリページ → Settings → Actions → Runners → New self-hosted runner
   ```

2. **サーバーにランナーをインストール**
   
   Linux/Macの場合：
   ```bash
   # ランナーディレクトリの作成
   mkdir actions-runner && cd actions-runner
   
   # ランナーのダウンロード（GitHubの指示に従う）
   curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
   tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz
   
   # ランナーの設定（GitHubで表示されるトークンを使用）
   ./config.sh --url https://github.com/YOUR_USERNAME/create_short --token YOUR_TOKEN
   
   # サービスとしてインストール
   sudo ./svc.sh install
   sudo ./svc.sh start
   ```

3. **必要なサービスの起動**
   
   ```bash
   # Ollamaの起動
   ollama serve &
   
   # VOICEVOXの起動（Docker）
   docker run -d --name voicevox \
     -p 50021:50021 \
     --restart unless-stopped \
     voicevox/voicevox_engine:cpu-ubuntu20.04-latest
   ```

### 2. GitHub Secretsの設定

リポジトリの Settings → Secrets and variables → Actions で以下を設定：

| Secret名 | 説明 | 必須 |
|---------|------|------|
| `GEMINI_API_KEY` | Google Gemini APIキー（AI台本生成用） | **推奨**（GitHub Actions実行時） |
| `PEXELS_API_KEY` | Pexels APIキー | オプション（config.pyに設定済み） |
| `PIXABAY_API_KEY` | Pixabay APIキー（フォールバック用） | オプション |
| `OLLAMA_MODEL` | 使用するOllamaモデル | オプション（デフォルト: gemma2:9b） |

#### API キーの取得方法

**Google Gemini API**（無料・推奨）:
1. https://aistudio.google.com/app/apikey にアクセス
2. Googleアカウントでログイン
3. 「Create API key」をクリック
4. 生成されたAPIキーをコピー
5. **無料枠**: 月100万トークン（十分な量）
6. **メリット**: セルフホストランナー不要、完全クラウド実行可能

**Pexels API**（無料）:
1. https://www.pexels.com/api/ にアクセス
2. アカウント作成
3. API Keyを取得

**Pixabay API**（無料、オプション）:
1. https://pixabay.com/api/docs/ にアクセス
2. アカウント作成
3. API Keyを取得

#### GitHub Secretsの登録方法

1. リポジトリページの **Settings** タブをクリック
2. 左サイドバーから **Secrets and variables** → **Actions** を選択
3. **New repository secret** をクリック
4. **Name** に `GEMINI_API_KEY` を入力
5. **Secret** に取得したAPIキーを貼り付け
6. **Add secret** をクリック

### 3. AI台本生成サービスの選択

#### GitHub Actionsでの推奨構成

**パターン1: Gemini API（完全クラウド実行・推奨）**
- `GEMINI_API_KEY` をGitHub Secretsに設定
- セルフホストランナー不要
- 完全無料（月100万トークン）
- Ollama不要でクラウドランナー（ubuntu-latest）で実行可能

**パターン2: Ollama（セルフホストランナー）**
- セルフホストランナーをセットアップ
- Ollamaをサーバーにインストール・起動
- `GEMINI_API_KEY` 未設定の場合、自動的にOllamaを使用

**パターン3: ハイブリッド（推奨）**
- `GEMINI_API_KEY` を設定
- Gemini API失敗時、自動的にOllamaにフォールバック（セルフホストランナーの場合）
- 高い可用性を実現

#### AI サービスの優先順位

台本生成時、以下の優先順位でAIサービスを選択：
1. **Google Gemini API** (`GEMINI_API_KEY` 設定時)
2. **OpenAI API** (`OPENAI_API_KEY` 設定時)
3. **Anthropic Claude API** (`ANTHROPIC_API_KEY` 設定時)
4. **Ollama** (ローカルLLM)
5. テンプレートフォールバック

### 4. ワークフローの有効化

1. リポジトリの **Actions** タブへ移動
2. 「毎日動画生成」ワークフローを選択
3. **Enable workflow** をクリック

## 🎮 使い方

### 手動実行

1. リポジトリの **Actions** タブを開く
2. 左側から「毎日動画生成」を選択
3. **Run workflow** → **Run workflow** をクリック

### 自動実行の確認

- **実行履歴**: Actions タブで過去の実行を確認
- **ログ確認**: 各実行をクリックして詳細ログを表示
- **生成物のダウンロード**: Artifacts から動画ファイルをダウンロード

## 📦 生成されるアーティファクト

ワークフロー実行後、以下がダウンロード可能になります：

- `generated-videos-{実行番号}/`
  - `data/videos/draft/*.mp4` - 生成された動画
  - `data/upload/descriptions_*.txt` - YouTube/TikTok用説明文
  - `data/logs/generation/*.log` - 実行ログ

アーティファクトは7日間保存されます。

## 🕐 スケジュール変更

実行時刻を変更する場合は `.github/workflows/daily-video-generation.yml` を編集：

```yaml
on:
  schedule:
    # cron形式: '分 時 日 月 曜日'
    # 例: 毎日 UTC 12:00 (日本時間 21:00) に実行
    - cron: '0 12 * * *'
```

### cron記法の例

| スケジュール | cron式 |
|------------|--------|
| 毎日 6:00 AM JST | `0 21 * * *` (UTC 21:00) |
| 毎日 12:00 PM JST | `0 3 * * *` (UTC 3:00) |
| 平日のみ 6:00 AM JST | `0 21 * * 1-5` |
| 週1回（月曜 6:00 AM JST） | `0 21 * * 1` |

**注意**: GitHub Actionsはすべて **UTC** タイムゾーンで動作します。日本時間 (JST) から9時間引いた値を設定してください。

## 🐛 トラブルシューティング

### ワークフローが失敗する

**原因1: サービスが起動していない**
```bash
# セルフホストランナーで確認
curl http://127.0.0.1:50021/speakers  # VOICEVOX
curl http://127.0.0.1:11434/api/tags  # Ollama
```

**原因2: ディスク容量不足**
```bash
df -h  # ディスク使用量確認
```

**原因3: 権限エラー**
```bash
# ランナーユーザーに適切な権限を付与
sudo usermod -aG docker actions-runner
```

### 動画が生成されない

1. **Actions タブでログを確認**
   - ワークフロー実行 → ステップごとのログを確認

2. **手動実行でテスト**
   ```bash
   # ランナーサーバーで直接実行
   cd /path/to/create_short
   python daily_generation.py
   ```

3. **API キーの確認**
   - Secrets が正しく設定されているか確認
   - API使用量制限に達していないか確認

### アーティファクトがダウンロードできない

- ワークフローが完了するまで待つ（最大2時間）
- ストレージ容量を確認（アーティファクトは7日後に自動削除）

## 📊 モニタリング

### GitHub Actions の使用状況確認

```
リポジトリ → Settings → Billing and plans → Usage this month
```

- **無料枠**: パブリックリポジトリは無制限
- **プライベートリポジトリ**: 月2,000分まで無料（セルフホストランナーは無制限）

### 実行統計の確認

```
リポジトリ → Insights → Actions
```

- 実行成功率
- 平均実行時間
- ワークフロー実行回数

## 🔒 セキュリティのベストプラクティス

1. **Secretsの使用**
   - API キーは必ずGitHub Secretsに保存
   - コード内にハードコードしない

2. **セルフホストランナーの保護**
   - ファイアウォールで不要なポートを閉じる
   - 定期的にランナーソフトウェアを更新

3. **アクセス制御**
   - プライベートリポジトリを推奨
   - 必要なメンバーのみにアクセス権を付与

## 🚀 次のステップ

セットアップ完了後、以下も検討してください：

1. **YouTube 自動アップロード**
   - [YouTube API設定ガイド](YOUTUBE_API_SETUP.md)参照
   - ワークフローにアップロードステップを追加

2. **通知の設定**
   - Slack/Discord への実行結果通知
   - エラー時のメール通知

3. **パフォーマンス最適化**
   - キャッシュの活用
   - 並列実行の検討

## 📚 関連ドキュメント

- [GitHub Actions公式ドキュメント](https://docs.github.com/ja/actions)
- [セルフホストランナーガイド](https://docs.github.com/ja/actions/hosting-your-own-runners)
- [ワークフロー構文リファレンス](https://docs.github.com/ja/actions/reference/workflow-syntax-for-github-actions)
