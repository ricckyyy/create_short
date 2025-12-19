# Windows タスクスケジューラ設定手順

## エラーが出た場合

PowerShellで以下を実行してください（管理者権限）:

```powershell
# 実行ポリシーを一時的に変更
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# その後、スクリプト実行
cd \\wsl$\Ubuntu\home\rt\create_short\scripts
.\setup_windows_task.ps1
```

## または、直接コマンドで設定

以下をPowerShell（管理者権限）にコピペして実行:

```powershell
# タスクアクション
$action = New-ScheduledTaskAction -Execute "wsl" -Argument "-d Ubuntu -u rt -- bash -c 'cd /home/rt/create_short && ./scripts/run_daily.sh >> data/logs/cron/cron_output.log 2>&1'"

# トリガー（毎日6:00AM）
$trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM

# 設定
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -WakeToRun -ExecutionTimeLimit (New-TimeSpan -Hours 2) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)

# プリンシパル
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest

# タスク登録
Register-ScheduledTask -TaskName "TikTok_VideoGeneration" -Description "毎日6:00AMに動画を自動生成" -Action $action -Trigger $trigger -Settings $settings -Principal $principal

# 確認
Get-ScheduledTask -TaskName "TikTok_VideoGeneration"

# テスト実行
Start-ScheduledTask -TaskName "TikTok_VideoGeneration"
```

## 設定完了後の確認

```powershell
# タスク状態確認
Get-ScheduledTaskInfo -TaskName "TikTok_VideoGeneration"

# ログ確認（WSL側）
wsl -d Ubuntu -u rt -- tail -f /home/rt/create_short/data/logs/cron/cron_output.log
```
