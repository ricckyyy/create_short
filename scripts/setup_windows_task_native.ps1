# Windows ネイティブ タスクスケジューラ 自動設定スクリプト
# WSLを使わず、Windowsネイティブ環境で直接Python実行
# 管理者権限のPowerShellで実行してください

Write-Host "================================" -ForegroundColor Cyan
Write-Host "TikTok動画生成 タスクスケジューラ設定 (Windowsネイティブ版)" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# プロジェクトパスの設定（環境に合わせて変更してください）
$ProjectPath = "G:\dev\create_short"
$PythonExe = "python"  # Pythonがパスに通っている場合
# $PythonExe = "C:\Users\rt\AppData\Local\Programs\Python\Python312\python.exe"  # 絶対パス指定も可能

# タスク名
$TaskName = "TikTok_VideoGeneration_Native"

# プロジェクトパスの存在確認
if (-not (Test-Path $ProjectPath)) {
    Write-Host "エラー: プロジェクトパスが見つかりません: $ProjectPath" -ForegroundColor Red
    Write-Host "スクリプト内の `$ProjectPath を正しいパスに変更してください" -ForegroundColor Yellow
    exit 1
}

# Python実行確認
try {
    $pythonVersion = & $PythonExe --version 2>&1
    Write-Host "Python検出: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "エラー: Pythonが見つかりません" -ForegroundColor Red
    Write-Host "スクリプト内の `$PythonExe を正しいパスに変更してください" -ForegroundColor Yellow
    exit 1
}

# 既存タスクを削除（エラーは無視）
try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "既存タスクを削除しました" -ForegroundColor Yellow
} catch {
    # 何もしない
}

# ログディレクトリ作成
$LogDir = Join-Path $ProjectPath "data\logs\cron"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    Write-Host "ログディレクトリを作成しました: $LogDir" -ForegroundColor Green
}

$LogFile = Join-Path $LogDir "cron_output.log"

# タスクアクション（実行するコマンド）
# Windowsネイティブ環境でPythonを直接実行
# 出力をログファイルにリダイレクト
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$ProjectPath'; & '$PythonExe' daily_generation.py 2>&1 | Tee-Object -FilePath '$LogFile' -Append`"" `
    -WorkingDirectory $ProjectPath

# トリガー（実行タイミング）
$trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM

# 設定（詳細オプション）
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -WakeToRun `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

# プリンシパル（実行ユーザー設定）
# ログオンしていなくても実行可能に変更
$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType S4U `
    -RunLevel Highest

# タスク登録
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "TikTok/YouTube Shorts用動画を毎日自動生成（Windowsネイティブ版、画面ロック時も実行）" | Out-Null
    
    Write-Host ""
    Write-Host "✅ タスクスケジューラ設定完了！" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "❌ タスク登録エラー" -ForegroundColor Red
    Write-Host "エラー内容: $_" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "【対処方法】" -ForegroundColor Cyan
    Write-Host "1. PowerShellを「管理者として実行」で起動"
    Write-Host "2. このスクリプトを再実行"
    Write-Host "3. パスワード入力を求められた場合は、Windowsログインパスワードを入力"
    exit 1
}
Write-Host ""
Write-Host "【設定内容】" -ForegroundColor Cyan
Write-Host "タスク名      : $TaskName"
Write-Host "実行時刻      : 毎日 6:00 AM"
Write-Host "実行方法      : PowerShell経由でPython実行"
Write-Host "作業ディレクトリ: $ProjectPath"
Write-Host "ログファイル  : $LogFile"
Write-Host "特権レベル    : 最上位（管理者権限）"
Write-Host "ログオンタイプ: パスワード保存（画面ロック時も実行）"
Write-Host ""
Write-Host "【重要】スリープ解除設定" -ForegroundColor Yellow
Write-Host "✅ タスク実行時にスリープを自動解除する設定を有効化済み"
Write-Host "⚠️ BIOS/UEFIで「Wake on RTC」が有効になっている必要があります"
Write-Host ""
Write-Host "【確認方法】" -ForegroundColor Cyan
Write-Host "1. タスクスケジューラを開く（Win + R → taskschd.msc）"
Write-Host "2. 「$TaskName」を検索"
Write-Host "3. 右クリック → 「実行する」でテスト可能"
Write-Host "4. 条件タブで「タスクを実行するためにスリープを解除する」にチェックが入っていることを確認"
Write-Host ""
Write-Host "【手動実行テスト】" -ForegroundColor Cyan
Write-Host "cd $ProjectPath"
Write-Host "$PythonExe daily_generation.py"
Write-Host ""

# オプション: テスト実行を提案
$testRun = Read-Host "今すぐテスト実行しますか？ (y/N)"
if ($testRun -eq "y" -or $testRun -eq "Y") {
    Write-Host ""
    Write-Host "テスト実行中..." -ForegroundColor Yellow
    Set-Location $ProjectPath
    & $PythonExe daily_generation.py
    Write-Host ""
    Write-Host "テスト実行完了" -ForegroundColor Green
}
