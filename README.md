# 🎬 ショート動画生成ツール（Webアプリ版 + 自動化対応）

TikTok/YouTube Shorts向けの縦型動画（720x1280）を自動生成するWebアプリケーションです。
**毎日自動で台本を変えて動画を生成する機能も搭載！**

## 🌟 機能

### 💻 Webアプリ機能
- **3つのアカウントプリセット**
  - 心理テストラボ（性格診断・心理テスト）
  - 闇夜の語り部（怖い話・都市伝説）
  - 映画紹介（映画レビュー）

- **自動生成パイプライン**
  - VOICEVOX TTS による音声生成
  - Pexels API による動画素材取得
  - 字幕自動付与
  - 縦型動画（720x1280）出力

- **Webインターフェース**
  - ブラウザから台本入力
  - リアルタイム進捗表示
  - 動画プレビュー・ダウンロード

### 🤖 自動化機能（NEW!）
- **AI台本自動生成**
  - OpenAI GPT-4 / Anthropic Claude 対応
  - アカウント別のプロンプト最適化
  - 毎日異なるコンテンツを自動生成

- **スケジュール実行**
  - cronによる定時自動実行
  - 完全無人運用が可能
  - 実行ログの自動記録

- **履歴管理**
  - 台本の自動保存
  - 重複防止機能
  - JSON形式でのデータ管理

## 📋 必要要件

### システム要件
- Python 3.8以上
- VOICEVOX Engine（ローカルで起動）
- tmux（バックグラウンド実行用）

### API キー
- Pexels API キー（`create_movie.py` に設定済み）

## 🚀 セットアップ

### 1. リポジトリのクローン
```bash
git clone <repository_url>
cd create_short
```

### 2. 仮想環境の作成と有効化
```bash
python3 -m venv ~/myenv
source ~/myenv/bin/activate
```

### 3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 4. VOICEVOX Engineのセットアップ
- [VOICEVOX Engine](https://github.com/VOICEVOX/voicevox_engine)をダウンロード
- `~/voicevox_engine-linux-cpu-x64-0.24.1/linux-cpu-x64/` に配置

## 🎮 使い方

### Webアプリの起動
```bash
./scripts/start_webapp.sh
```

ブラウザで `http://localhost:5000` を開きます。

### 自動生成システムのテスト（API不要）
```bash
./scripts/test_generation.sh
```

### cronで毎日自動実行を設定
```bash
./scripts/setup_cron.sh
```

### コマンドライン版（従来）
```bash
source ~/myenv/bin/activate
python create_movie.py
```

## 🤖 自動化セットアップ（詳細は `docs/AUTOMATION_GUIDE.md` 参照）

### 1. APIキーの設定（オプション）

AIで台本を自動生成する場合は、APIキーを設定：

```bash
# OpenAI を使う場合
export OPENAI_API_KEY="your-openai-api-key"
pip install openai

# または Anthropic Claude を使う場合
export ANTHROPIC_API_KEY="your-anthropic-api-key"
pip install anthropic
```

**APIなしでも動作可能**：テンプレートモードで自動実行できます

### 2. テスト実行
```bash
./scripts/test_generation.sh
```

### 3. 自動実行の設定
```bash
./scripts/setup_cron.sh
```

毎日午前6時に自動で動画が生成されます！

## 📖 Webアプリの使い方

1. **プリセット選択**（オプション）
   - 3つのアカウントから選択
   - キーワードが自動入力されます

2. **台本入力**
   - アカウント名を入力
   - 台本を改行区切りで入力（10行程度推奨）
   - キーワードをカンマ区切りで入力

3. **動画生成**
   - 「動画を生成」ボタンをクリック
   - 進捗バーで状況を確認

4. **ダウンロード**
   - 生成完了後、動画一覧からダウンロード

## 📁 プロジェクト構成

```
create_short/
├── app.py                          # Flask Webアプリ
├── create_movie.py                 # コア動画生成ロジック
├── generate_script.py              # AI台本生成スクリプト
├── daily_generation.py             # 日次自動生成メインスクリプト
├── requirements.txt                # Python依存パッケージ
├── start_webapp.sh                 # Webアプリ起動スクリプト
├── run_daily.sh                    # 日次実行ラッパー（cron用）
├── test_generation.sh              # テスト実行スクリプト
├── setup_cron.sh                   # cron自動設定スクリプト
├── README.md                       # このファイル
├── AUTOMATION_GUIDE.md             # 自動化の詳細ガイド
├── daihon.md                       # 台本作成ガイドライン
├── templates/
│   └── index.html                  # Webアプリフロントエンド
├── output/                         # 生成動画の出力先
├── script_history/                 # 台本履歴（自動生成）
└── logs/                           # 実行ログ（自動生成）
```

## 🎯 台本作成のコツ

詳細は `daihon.md` を参照してください。

- **冒頭2秒でフック**: 視聴者の興味を引く
- **10行程度**: 視聴維持率を意識した長さ
- **CTA**: 最後にフォロー・コメント促進
- **トーン統一**: アカウントの特性に合わせる

## 🔧 カスタマイズ

### 話者の変更
`create_movie.py` の以下の部分を編集：
```python
if acc["name"] == "闇夜の語り部":
    speaker_index = 7  # 青山龍星（低い声）
    pitch = -0.5
else:
    speaker_index = 1  # ずんだもん
    pitch = 0
```

### フォント変更
`create_subtitle_image()` 関数内のフォントパスを変更

## 🐛 トラブルシューティング

### VOICEVOX接続エラー
```bash
# VOICEVOXが起動しているか確認
curl http://127.0.0.1:50021/speakers

# 手動起動
cd ~/voicevox_engine-linux-cpu-x64-0.24.1/linux-cpu-x64
./run
```

### モジュールが見つからない
```bash
source ~/myenv/bin/activate
pip install -r requirements.txt
```

### 動画が生成されない
- Pexels APIキーを確認
- `output/` ディレクトリが存在するか確認
- キーワード数が台本行数以上あるか確認

### 自動実行が動かない
```bash
# ログ確認
tail -f logs/cron_output.log

# cron設定確認
crontab -l

# 手動テスト実行
./test_generation.sh
```

## 📚 詳細ドキュメント

### 📖 基本ガイド
- **[クイックスタート](docs/QUICKSTART.md)** - 最速で動画生成を始める手順
- **[台本作成ガイド](docs/daihon.md)** - エンゲージメントを高める台本作成のコツ
- **[フォルダ構造](docs/FOLDER_STRUCTURE.md)** - プロジェクトのディレクトリ構成説明

### 🤖 自動化
- **[自動化ガイド](docs/AUTOMATION_GUIDE.md)** - cronによる毎日自動生成の設定方法
- **[台本生成](docs/SCRIPT_GENERATION.md)** - AI台本生成機能の使い方（Ollama/OpenAI/Claude）
- **[Windows自動化](docs/WINDOWS_TASK_SCHEDULER.md)** - Windowsタスクスケジューラでの自動実行

### 📊 アナリティクス（NEW!）
- **[アナリティクス機能](docs/ANALYTICS_GUIDE.md)** - 再生数分析とAI学習による台本最適化

### 📤 YouTube連携
- **[YouTube API設定](docs/YOUTUBE_API_SETUP.md)** - YouTube Data API v3のセットアップ手順
- **[YouTube自動投稿](docs/YOUTUBE_UPLOAD_GUIDE.md)** - 動画の自動アップロード設定

### 🔧 開発者向け
- **[Git運用ルール](docs/GIT_WORKFLOW.md)** - GitHub Flowに基づく開発フロー
- **[プロジェクトファイル](docs/PROJECT_FILES.md)** - 各ファイルの役割と責務

## 🎯 運用フロー

### 初回セットアップ
1. 依存パッケージをインストール
2. VOICEVOX Engineをセットアップ
3. （オプション）APIキーを設定
4. テスト実行で動作確認
5. cronジョブを設定

### 日常運用
- **完全自動**: 設定した時刻に自動で動画生成
- **手動生成**: Webアプリからいつでも生成可能
- **定期確認**: 週1回ログをチェック

### メンテナンス
- ディスク容量の監視
- 古い動画/ログの削除
- API使用量の確認（有料プラン使用時）

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🙏 謝辞

- [VOICEVOX](https://voicevox.hiroshiba.jp/) - 音声合成エンジン
- [Pexels](https://www.pexels.com/) - 動画素材提供
- [MoviePy](https://zulko.github.io/moviepy/) - 動画編集ライブラリ
