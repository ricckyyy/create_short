# 🚀 クイックスタートガイド

毎日自動で動画を生成するための最速セットアップ手順

## ⚡ 3ステップで自動化開始

### Step 1: テスト実行
```bash
cd /home/rt/create_short
./test_generation.sh
```

✅ 動画が3つ生成されれば成功！

### Step 2: cron設定
```bash
./setup_cron.sh
```

質問に `y` と答えるだけ

### Step 3: 完了！
明日の午前6時から、毎日自動で動画が生成されます 🎉

---

## 📊 確認コマンド

### 今日の動画を見る
```bash
ls -lh output/
```

### ログを確認
```bash
tail -f logs/cron_output.log
```

### cron設定を確認
```bash
crontab -l
```

---

## 🎨 カスタマイズ（オプション）

### 実行時刻を変更したい
```bash
crontab -e
```

例：午後9時に変更
```
0 21 * * * /home/rt/create_short/run_daily.sh >> /home/rt/create_short/logs/cron_output.log 2>&1
```

### AI APIで台本を生成したい
```bash
# OpenAIの場合
echo 'export OPENAI_API_KEY="sk-xxxx"' >> ~/.bashrc
source ~/.bashrc
pip install openai

# Claudeの場合
echo 'export ANTHROPIC_API_KEY="sk-ant-xxxx"' >> ~/.bashrc
source ~/.bashrc
pip install anthropic
```

### Webアプリも使いたい
```bash
./start_webapp.sh
```

ブラウザで `http://localhost:5000` を開く

---

## 🆘 問題が起きたら

### 動画が生成されない
```bash
# 手動実行でエラー確認
cd /home/rt/create_short
source ~/myenv/bin/activate
python3 daily_generation.py
```

### VOICEVOXエラー
```bash
# VOICEVOXを再起動
tmux kill-session -t voicevox
tmux new-session -d -s voicevox 'cd ~/voicevox_engine-linux-cpu-x64-0.24.1/linux-cpu-x64 && ./run'
```

### 詳しいヘルプ
```bash
cat AUTOMATION_GUIDE.md
```

---

## 📝 生成される動画

- `output/心理テストラボ_YYYYMMDD.mp4`
- `output/闇夜の語り部_YYYYMMDD.mp4`
- `output/映画紹介_YYYYMMDD.mp4`

毎日新しいコンテンツが自動生成されます！

---

**これで完了です！後は自動で動画が生成されるのを待つだけ 🎬**
