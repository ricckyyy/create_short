# GitHub Actions クイックスタートガイド

このガイドでは、GitHub Actionsを使って毎日6時に自動で動画を生成する方法を**最短で**説明します。

## 🚀 最速セットアップ（5分）

### ステップ1️⃣: ワークフローを有効化

1. GitHubリポジトリのページを開く
2. **「Actions」** タブをクリック
3. 「毎日動画生成」を選択
4. **「Enable workflow」** をクリック

### ステップ2️⃣: 実行方法を選択

#### 方法A: セルフホストランナー（推奨）

**必要なもの**:
- 常時稼働できるサーバー（自宅PC/VPS等）
- Docker
- Ollama

**セットアップ手順**:
```bash
# 1. GitHubでランナーを追加
# リポジトリ → Settings → Actions → Runners → New self-hosted runner

# 2. サーバーでランナーをインストール
mkdir actions-runner && cd actions-runner
# GitHubに表示されるコマンドを実行

# 3. 必要なサービスを起動
ollama serve &
docker run -d --name voicevox -p 50021:50021 voicevox/voicevox_engine:cpu-ubuntu20.04-latest

# 4. ランナーをサービスとして起動
sudo ./svc.sh install
sudo ./svc.sh start
```

**メリット**: 安定動作、ストレージ容量に余裕

#### 方法B: GitHub-hostedランナー（実験的）

**必要なもの**:
- なし（GitHub側で実行）

**セットアップ手順**:
1. `.github/workflows/daily-video-generation-cloud.yml` の schedule セクションのコメントを解除
2. 実行時間が長い（初回は30分以上かかる可能性あり）

**メリット**: サーバー不要

### ステップ3️⃣: 手動テスト実行

1. **Actions** タブを開く
2. 「毎日動画生成」をクリック
3. **「Run workflow」** をクリック
4. **「Run workflow」** をもう一度クリック
5. 実行が開始される（進捗を確認可能）

### ステップ4️⃣: 生成された動画をダウンロード

1. 実行が完了したら、そのワークフローをクリック
2. **「Artifacts」** セクションにある `generated-videos-XXX` をクリック
3. ZIPファイルがダウンロードされる
4. 解凍すると以下が含まれる：
   - 動画ファイル（`.mp4`）
   - 説明文（`.txt`）
   - ログファイル（`.log`）

## 🎯 実行スケジュール

デフォルト設定:
- **毎日 6:00 AM（日本時間）** に自動実行
- UTC 21:00 = JST 6:00 AM

### スケジュールを変更したい場合

`.github/workflows/daily-video-generation.yml` を編集:

```yaml
schedule:
  - cron: '0 21 * * *'  # ← この行を変更
```

**よく使う設定例**:
```yaml
# 毎日 9:00 AM JST
- cron: '0 0 * * *'

# 平日のみ 6:00 AM JST
- cron: '0 21 * * 1-5'

# 週1回（月曜 6:00 AM JST）
- cron: '0 21 * * 1'
```

💡 **Tip**: JSTからUTCに変換するには、**9時間引く**
- JST 6:00 → UTC 21:00 (前日)
- JST 12:00 → UTC 3:00

## 🔑 API キーの設定（オプション）

Pexels APIキーは `config.py` にハードコードされていますが、Secretsで上書き可能:

1. リポジトリ → **Settings** → **Secrets and variables** → **Actions**
2. **「New repository secret」** をクリック
3. 以下を追加:

| Name | Value |
|------|-------|
| `PEXELS_API_KEY` | あなたのPexels APIキー |
| `PIXABAY_API_KEY` | あなたのPixabay APIキー（オプション） |
| `OLLAMA_MODEL` | 使用するモデル（例: `gemma2:9b`） |

## ❓ よくある質問

### Q: 無料で使える？

**A:** はい！
- パブリックリポジトリ: **完全無料**
- プライベートリポジトリ: 月2,000分まで無料
- セルフホストランナー: **無制限**（自分のサーバーを使うため）

### Q: 動画はどこに保存される？

**A:** 
- **Artifacts**: 7日間保存（自動削除）
- **ダウンロード**: 手動で保存する必要あり
- セルフホストランナーの場合、サーバーの `data/videos/draft/` にも保存

### Q: 実行に失敗した場合は？

**A:**
1. **Actions** タブで該当する実行をクリック
2. 赤くなっているステップをクリック
3. ログを確認
4. よくあるエラー:
   - VOICEVOX起動失敗 → サービスが起動しているか確認
   - Ollama接続失敗 → モデルがプルされているか確認
   - API制限 → API使用量を確認

### Q: セルフホストランナーは必須？

**A:** いいえ。
- **推奨**: セルフホストランナー（安定性が高い）
- **代替**: GitHub-hostedランナー（実験的、初回は時間がかかる）

## 📚 詳細情報

より詳しい情報は以下を参照:
- [完全版セットアップガイド](GITHUB_ACTIONS_SETUP.md)
- [GitHub Actions公式ドキュメント](https://docs.github.com/ja/actions)

## 🎉 完了！

これで毎日自動で動画が生成されるようになりました！

**次にやること**:
1. Actions タブで実行履歴を確認
2. 生成された動画をダウンロード
3. YouTube/TikTokに投稿

お疲れ様でした！ 🚀
