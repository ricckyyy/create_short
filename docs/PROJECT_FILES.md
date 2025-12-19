# 📂 プロジェクトファイル一覧

## コアスクリプト

| ファイル | 説明 |
|---------|------|
| `config.py` | 設定・パス管理（全パスを一元管理） |
| `create_movie.py` | 動画生成コア（音声合成+動画編集） |
| `generate_script.py` | AI台本自動生成 |
| `daily_generation.py` | 日次自動生成メイン |
| `app.py` | Flask Webアプリ |

## 実行スクリプト

| ファイル | 説明 | 使い方 |
|---------|------|--------|
| `start_webapp.sh` | Webアプリ起動 | `./start_webapp.sh` |
| `run_daily.sh` | 日次生成実行（cron用） | `./run_daily.sh` |
| `test_generation.sh` | テスト実行 | `./test_generation.sh` |
| `setup_cron.sh` | cron自動設定 | `./setup_cron.sh` |
| `start_shell.sh` | 開発環境起動 | `./start_shell.sh` |

## ドキュメント

| ファイル | 内容 |
|---------|------|
| `README.md` | プロジェクト全体の概要 |
| `QUICKSTART.md` | 3ステップセットアップガイド |
| `AUTOMATION_GUIDE.md` | 自動化の詳細ガイド |
| `FOLDER_STRUCTURE.md` | ディレクトリ構造の説明 |
| `daihon.md` | 台本作成ガイドライン |

## 設定ファイル

| ファイル | 説明 |
|---------|------|
| `requirements.txt` | Python依存パッケージ |
| `.github/copilot-instructions.md` | AI Coding Agent向け指示 |

## データディレクトリ (`data/`)

| ディレクトリ | 内容 |
|------------|------|
| `videos/draft/` | 生成された動画（投稿前） |
| `videos/published/` | 投稿済み動画 |
| `scripts/history/` | 台本履歴 |
| `logs/generation/` | 生成ログ |
| `audio/` | 一時音声（自動削除） |
| `assets/video_clips/` | ダウンロード素材（自動削除） |

## テンプレート

| ファイル | 説明 |
|---------|------|
| `templates/index.html` | Webアプリフロントエンド |

---

**合計16ファイル + data/ディレクトリ = クリーンな構成！**
