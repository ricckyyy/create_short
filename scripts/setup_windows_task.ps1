# Windows タスクスケジューラ 自動設定スクリプト
# 管理者権限のPowerShellで実行してください

Write-Host "================================" -ForegroundColor Cyan
Write-Host "TikTok動画生成 タスクスケジューラ設定" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 既存タスクを削除（エラーは無視）
try {
    Unregister-ScheduledTask -TaskName "TikTok_VideoGeneration" -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "既存タスクを削除しました" -ForegroundColor Yellow
} catch {
    # 何もしない
}

# タスクアクション（実行するコマンド）
$action = New-ScheduledTaskAction `
    -Execute "wsl" `
    -Argument "-d Ubuntu -u rt -- bash -c 'cd /home/rt/create_short && ./scripts/run_daily.sh >> data/logs/cron/cron_output.log 2>&1'"

# トリガー（実行タイミング）
$trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM

# 設定（詳細オプション）
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -WakeToRun `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5)

# プリンシパル（実行ユーザー）
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType S4U `
    -RunLevel Highest

# タスク登録
try {
    Register-ScheduledTask `
        -TaskName "TikTok_VideoGeneration" `
        -Description "毎日6:00AMに動画を自動生成してTikTok/YouTube Shortsに投稿" `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -ErrorAction Stop

    Write-Host ""
    Write-Host "✅ タスクスケジューラに登録完了！" -ForegroundColor Green
    Write-Host ""
    Write-Host "設定内容:" -ForegroundColor Cyan
    Write-Host "  - タスク名: TikTok_VideoGeneration" -ForegroundColor White
    Write-Host "  - 実行時刻: 毎日 午前 6:00" -ForegroundColor White
    Write-Host "  - スリープ復帰: 有効" -ForegroundColor White
    Write-Host "  - バッテリー駆動: 有効" -ForegroundColor White
    Write-Host "  - 失敗時の再試行: 3回（5分間隔）" -ForegroundColor White
    Write-Host ""

    # タスク情報を表示
    Write-Host "登録されたタスク:" -ForegroundColor Cyan
    Get-ScheduledTask -TaskName "TikTok_VideoGeneration" | Format-Table -AutoSize

    Write-Host ""
    Write-Host "テスト実行しますか? (y/n): " -ForegroundColor Yellow -NoNewline
    $response = Read-Host

    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host ""
        Write-Host "テスト実行中..." -ForegroundColor Cyan
        Start-ScheduledTask -TaskName "TikTok_VideoGeneration"
        Start-Sleep -Seconds 2
        
        Write-Host ""
        Write-Host "タスク状態:" -ForegroundColor Cyan
        Get-ScheduledTaskInfo -TaskName "TikTok_VideoGeneration" | Format-List
        
        Write-Host ""
        Write-Host "WSLでログを確認してください:" -ForegroundColor Yellow
        Write-Host "  wsl -d Ubuntu -u rt -- tail -f /home/rt/create_short/data/logs/cron/cron_output.log" -ForegroundColor White
    }

} catch {
    Write-Host ""
    Write-Host "❌ エラーが発生しました: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "管理者権限で実行していますか？" -ForegroundColor Yellow
    Write-Host "PowerShellを右クリック → '管理者として実行' で再度お試しください" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "完了" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
