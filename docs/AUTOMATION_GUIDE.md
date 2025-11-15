# 毎日自動動画生成システム

## 📅 自動化の仕組み

このシステムは、毎日決まった時間に自動で以下を実行します：
1. AI が3アカウント分の台本を生成
2. VOICEVOX で音声合成
3. Pexels から動画素材を取得
4. 字幕付き縦型動画を自動生成

## 🤖 AI台本生成の設定

### 対応API
- **OpenAI GPT-4** (推奨)
- **Anthropic Claude**
- **フォールバック**: APIなしでもランダムテンプレートで動作

### APIキーの設定

#### OpenAI を使う場合
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

#### Anthropic Claude を使う場合
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

#### 環境変数を永続化（推奨）
`~/.bashrc` または `~/.bash_profile` に追加：
```bash
echo 'export OPENAI_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 必要なパッケージのインストール
```bash
source ~/myenv/bin/activate

# OpenAI を使う場合
pip install openai

# Anthropic を使う場合
pip install anthropic
```

## ⏰ cron 設定

### 1. cronジョブの編集
```bash
crontab -e
```

### 2. スケジュール設定例

#### 毎日午前6時に実行
```cron
0 6 * * * /home/rt/create_short/run_daily.sh >> /home/rt/create_short/logs/cron_output.log 2>&1
```

#### 毎日午後9時に実行
```cron
0 21 * * * /home/rt/create_short/run_daily.sh >> /home/rt/create_short/logs/cron_output.log 2>&1
```

#### 平日の午前7時に実行
```cron
0 7 * * 1-5 /home/rt/create_short/run_daily.sh >> /home/rt/create_short/logs/cron_output.log 2>&1
```

#### 毎日2回（朝9時と夕方18時）
```cron
0 9,18 * * * /home/rt/create_short/run_daily.sh >> /home/rt/create_short/logs/cron_output.log 2>&1
```

### 3. cron設定の確認
```bash
crontab -l
```

### cron時刻フォーマット
```
* * * * * コマンド
│ │ │ │ │
│ │ │ │ └─ 曜日 (0-7, 0と7は日曜日)
│ │ │ └─── 月 (1-12)
│ │ └───── 日 (1-31)
│ └─────── 時 (0-23)
└───────── 分 (0-59)
```

## 🚀 手動実行

### テスト実行
```bash
cd /home/rt/create_short
source ~/myenv/bin/activate
python3 daily_generation.py
```

### ラッパースクリプトで実行
```bash
./run_daily.sh
```

## 📁 生成されるファイル

### ディレクトリ構成
```
create_short/
├── output/                          # 生成動画
│   ├── 心理テストラボ_20251108.mp4
│   ├── 闇夜の語り部_20251108.mp4
│   └── 映画紹介_20251108.mp4
├── script_history/                  # 台本履歴
│   ├── 心理テストラボ_20251108_060000.txt
│   ├── 闇夜の語り部_20251108_060000.txt
│   └── 映画紹介_20251108_060000.txt
├── logs/                            # 実行ログ
│   ├── daily_generation_20251108.log
│   ├── cron_execution.log
│   └── cron_output.log
└── daily_scripts_20251108.json     # 台本データ（JSON）
```

## 📊 ログの確認

### 最新の生成ログ
```bash
cat logs/daily_generation_$(date +%Y%m%d).log
```

### cron実行ログ
```bash
tail -f logs/cron_output.log
```

### リアルタイムで監視
```bash
watch -n 5 'tail -20 logs/daily_generation_$(date +%Y%m%d).log'
```

## 🔧 トラブルシューティング

### VOICEVOXが起動しない
```bash
# tmuxセッション確認
tmux ls

# 手動起動
cd ~/voicevox_engine-linux-cpu-x64-0.24.1/linux-cpu-x64
./run
```

### cronが実行されない
```bash
# cronサービス確認
sudo service cron status

# cronログ確認（Ubuntu/Debian）
sudo grep CRON /var/log/syslog

# 実行権限確認
ls -l /home/rt/create_short/run_daily.sh
```

### 動画が生成されない
```bash
# ログ確認
tail -100 logs/daily_generation_$(date +%Y%m%d).log

# 手動実行でデバッグ
cd /home/rt/create_short
source ~/myenv/bin/activate
python3 daily_generation.py
```

### API制限エラー
- OpenAI/Claude のAPI使用量・クォータを確認
- フォールバックモード（APIなし）でも動作可能

## 🎯 カスタマイズ

### 台本生成プロンプトの変更
`generate_script.py` の `ACCOUNT_PROMPTS` を編集

### 話者（声）の変更
`daily_generation.py` の `speaker_index` と `pitch` を調整

### キーワードの変更
`generate_script.py` の各アカウントの `keywords` リストを編集

### 生成頻度の変更
cronジョブの時刻設定を変更

## 🔐 セキュリティ

### APIキーの保護
```bash
# 環境変数ファイルのパーミッション制限
chmod 600 ~/.bashrc
```

### ログファイルの定期削除
```bash
# 30日以上古いログを削除（cronに追加）
0 3 * * 0 find /home/rt/create_short/logs -name "*.log" -mtime +30 -delete
```

## 📈 運用のベストプラクティス

1. **定期的な動作確認**: 週1回はログをチェック
2. **ディスク容量監視**: 動画ファイルが蓄積するため定期削除
3. **API使用量管理**: 月次でコストを確認
4. **バックアップ**: `script_history/` は定期バックアップ推奨
5. **エラー通知**: 失敗時にメール通知を設定（オプション）

## 🎬 次のステップ

1. APIキーを設定
2. テスト実行で動作確認
3. cronジョブを設定
4. 初日の実行結果を確認
5. 必要に応じてプロンプト調整

---

**自動化完了後は、毎日新しいコンテンツが自動生成されます！**
