# GitHub Actions セットアップチェックリスト

このチェックリストを使って、GitHub Actionsの設定が正しく完了しているか確認しましょう。

## 📋 事前確認

- [ ] GitHubアカウントを持っている
- [ ] リポジトリへの管理者権限がある
- [ ] 実行方法を選択した
  - [ ] セルフホストランナー（推奨）
  - [ ] GitHub-hostedランナー（実験的）

## 🔧 セルフホストランナーのセットアップ（選択した場合）

### サーバー準備
- [ ] 常時稼働できるサーバーを用意した
- [ ] サーバーがインターネットに接続されている
- [ ] Python 3.9以上がインストールされている
- [ ] Dockerがインストールされている
- [ ] Ollamaがインストールされている

### ランナーのインストール
- [ ] GitHubリポジトリの Settings → Actions → Runners を開いた
- [ ] "New self-hosted runner" をクリックした
- [ ] 表示される手順に従ってランナーをインストールした
- [ ] `./config.sh` を実行した
- [ ] `./svc.sh install` を実行した
- [ ] `./svc.sh start` を実行した
- [ ] ランナーが "Idle" 状態になっている

### サービスの起動
- [ ] Ollamaを起動した (`ollama serve`)
- [ ] Ollamaが起動していることを確認した
  ```bash
  curl http://127.0.0.1:11434/api/tags
  ```
- [ ] VOICEVOXコンテナを起動した
  ```bash
  docker run -d --name voicevox -p 50021:50021 voicevox/voicevox_engine:cpu-ubuntu20.04-latest
  ```
- [ ] VOICEVOXが起動していることを確認した
  ```bash
  curl http://127.0.0.1:50021/speakers
  ```

## ☁️ GitHub-hostedランナーのセットアップ（選択した場合）

- [ ] `.github/workflows/daily-video-generation-cloud.yml` の schedule セクションのコメントを解除した
- [ ] 初回実行に30分以上かかる可能性があることを理解した

## 🔑 GitHub Secrets の設定（オプション）

- [ ] リポジトリの Settings → Secrets and variables → Actions を開いた
- [ ] 以下のSecretsを設定した（必要に応じて）:
  - [ ] `PEXELS_API_KEY`（オプション、config.pyに設定済み）
  - [ ] `PIXABAY_API_KEY`（オプション）
  - [ ] `OLLAMA_MODEL`（オプション、デフォルト: gemma2:9b）

### API キーの取得（必要な場合）
- [ ] Pexels APIキーを取得した (https://www.pexels.com/api/)
- [ ] Pixabay APIキーを取得した (https://pixabay.com/api/docs/)（オプション）

## 📂 リポジトリの確認

- [ ] `.github/workflows/` ディレクトリが存在する
- [ ] `daily-video-generation.yml` ファイルが存在する
- [ ] `requirements.txt` ファイルが存在する
- [ ] `daily_generation.py` ファイルが存在する
- [ ] `config.py` ファイルが存在する

## ✅ ワークフローの有効化

- [ ] リポジトリの Actions タブを開いた
- [ ] ワークフローが表示されている
- [ ] 「Enable workflow」をクリックした（無効化されていた場合）

## 🧪 テスト実行

- [ ] Actions タブを開いた
- [ ] 「毎日動画生成」ワークフローを選択した
- [ ] 「Run workflow」ボタンをクリックした
- [ ] ワークフローが開始された
- [ ] 実行が完了した（緑のチェックマーク）
- [ ] Artifacts セクションに成果物が表示されている

### エラーが発生した場合
- [ ] 失敗したステップをクリックしてログを確認した
- [ ] エラーメッセージを読んで原因を特定した
- [ ] エラーを修正した
- [ ] 再度テスト実行した

## 📥 成果物の確認

- [ ] 実行完了後、Artifacts をクリックした
- [ ] `generated-videos-XXX` をダウンロードした
- [ ] ZIPファイルを解凍した
- [ ] 以下のファイルが含まれていることを確認した:
  - [ ] 動画ファイル (`.mp4`)
  - [ ] 説明文ファイル (`.txt`)
  - [ ] ログファイル (`.log`)

## 🔔 スケジュールの確認

- [ ] `.github/workflows/daily-video-generation.yml` を開いた
- [ ] schedule セクションの cron 式を確認した
  ```yaml
  schedule:
    - cron: '0 21 * * *'  # 毎日 JST 6:00 AM
  ```
- [ ] 実行時刻が希望通りか確認した
- [ ] 必要に応じて cron 式を変更した

## 📊 モニタリング設定

- [ ] Actions タブをブックマークした
- [ ] 実行失敗時のメール通知設定を確認した（Settings → Notifications）
- [ ] 定期的に実行履歴を確認する予定を立てた

## 🎓 ドキュメント確認

- [ ] `docs/GITHUB_ACTIONS_QUICKSTART.md` を読んだ
- [ ] `docs/GITHUB_ACTIONS_SETUP.md` を読んだ
- [ ] `docs/GITHUB_ACTIONS_ARCHITECTURE.md` を読んだ
- [ ] トラブルシューティングセクションを確認した

## ✨ 完了確認

- [ ] 手動実行が成功した
- [ ] 動画が正しく生成された
- [ ] Artifactsから動画をダウンロードできた
- [ ] スケジュール設定を確認した
- [ ] セルフホストランナー（使用している場合）が正常に動作している

## 🚀 次のステップ

- [ ] 最初の自動実行を待つ
- [ ] 翌日、実行履歴を確認する
- [ ] 生成された動画をYouTube/TikTokに投稿する
- [ ] パフォーマンスを監視する
- [ ] 必要に応じて設定を調整する

---

## ❓ 問題が発生した場合

以下を確認してください:

1. **サービスが起動しているか**
   ```bash
   curl http://127.0.0.1:11434/api/tags    # Ollama
   curl http://127.0.0.1:50021/speakers    # VOICEVOX
   ```

2. **ログを確認**
   - Actions タブで該当する実行をクリック
   - 赤くなっているステップをクリック
   - エラーメッセージを確認

3. **ディスク容量**
   ```bash
   df -h
   ```

4. **ドキュメントを参照**
   - [トラブルシューティング](GITHUB_ACTIONS_SETUP.md#-トラブルシューティング)
   - [FAQ](GITHUB_ACTIONS_QUICKSTART.md#-よくある質問)

---

**すべてのチェックボックスが完了したら、セットアップ完了です！** 🎉

お疲れ様でした！
