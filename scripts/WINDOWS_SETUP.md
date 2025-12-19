# 🪟 Windowsタスクスケジューラ セットアップ（簡易版）

## 🚀 自動設定（推奨）

### 1. PowerShellを管理者権限で開く

1. Windowsキー押下
2. 「PowerShell」と入力
3. 右クリック → **「管理者として実行」**

### 2. スクリプト実行

```powershell
cd \\wsl$\Ubuntu\home\rt\create_short\scripts
.\setup_windows_task.ps1
```

または、WSLから:

```bash
# Windowsエクスプローラーでスクリプトを開く
explorer.exe /home/rt/create_short/scripts/setup_windows_task.ps1
# 右クリック → "PowerShellで実行"（要管理者権限）
```

### 3. テスト実行

PowerShellで:
```powershell
# 今すぐ実行
Start-ScheduledTask -TaskName "TikTok_VideoGeneration"

# 状態確認
Get-ScheduledTaskInfo -TaskName "TikTok_VideoGeneration"
```

## 📋 設定内容

- **タスク名**: TikTok_VideoGeneration
- **実行時刻**: 毎日 午前 6:00
- **スリープ復帰**: ✅ 有効（PCがスリープから自動復帰して実行）
- **バッテリー駆動**: ✅ 有効
- **失敗時の再試行**: 3回（5分間隔）
- **タイムアウト**: 2時間

## 🔍 ログ確認

WSLで:
```bash
# リアルタイムでログ確認
tail -f ~/create_short/data/logs/cron/cron_output.log
```

Windowsで:
```powershell
# ログファイルを開く
notepad \\wsl$\Ubuntu\home\rt\create_short\data\logs\cron\cron_output.log
```

## ✅ 確認事項

- [ ] タスクが登録されている（タスクスケジューラで確認）
- [ ] テスト実行が成功する
- [ ] ログファイルに出力される
- [ ] VOICEVOXが起動する
- [ ] Ollamaが起動する
- [ ] 動画が生成される

## 🗑️ タスク削除

```powershell
Unregister-ScheduledTask -TaskName "TikTok_VideoGeneration" -Confirm:$false
```

---

詳細は [WINDOWS_TASK_SCHEDULER.md](../docs/WINDOWS_TASK_SCHEDULER.md) を参照
