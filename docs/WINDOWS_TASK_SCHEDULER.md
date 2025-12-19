# Windows タスクスケジューラ設定ガイド

## 📋 概要

WSL2のcronの代わりに、Windowsタスクスケジューラを使用することで、より確実な自動実行が可能になります。

## ⚙️ 自動設定（PowerShell）

### 1. PowerShellを管理者権限で開く

1. Windowsキー押下
2. "PowerShell" と入力
3. 右クリック → "管理者として実行"

### 2. 以下のコマンドを実行

```powershell
# タスクスケジューラに登録
$action = New-ScheduledTaskAction -Execute "wsl" -Argument "-d Ubuntu -u rt -- bash -c 'cd /home/rt/create_short && ./scripts/run_daily.sh >> data/logs/cron/cron_output.log 2>&1'"

$trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -WakeToRun `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5)

$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType S4U -RunLevel Highest

Register-ScheduledTask `
    -TaskName "TikTok_VideoGeneration" `
    -Description "毎日6:00AMに動画を自動生成してTikTok/YouTube Shortsに投稿" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal
```

### 3. 確認

```powershell
# タスクが登録されているか確認
Get-ScheduledTask -TaskName "TikTok_VideoGeneration"

# 今すぐテスト実行
Start-ScheduledTask -TaskName "TikTok_VideoGeneration"
```

## 🖱️ 手動設定（GUI）

### 1. タスクスケジューラを開く

1. Windowsキー + R
2. `taskschd.msc` と入力
3. Enter

### 2. 基本タスクの作成

1. 右側の「タスクの作成」をクリック
2. **全般タブ**:
   - 名前: `TikTok_VideoGeneration`
   - 説明: `毎日6:00AMに動画を自動生成`
   - ☑ 最上位の特権で実行する

### 3. トリガー設定

1. 「トリガー」タブ → 「新規」
2. タスクの開始: `スケジュールに従う`
3. 設定: `毎日`
4. 開始: `午前 6:00:00`
5. ☑ 有効
6. OK

### 4. 操作設定

1. 「操作」タブ → 「新規」
2. 操作: `プログラムの開始`
3. プログラム/スクリプト: `wsl`
4. 引数の追加:
   ```
   -d Ubuntu -u rt -- bash -c "cd /home/rt/create_short && ./scripts/run_daily.sh >> data/logs/cron/cron_output.log 2>&1"
   ```
5. OK

### 5. 条件設定

1. 「条件」タブ
2. ☐ コンピューターをAC電源で使用している場合のみタスクを開始する（チェックを外す）
3. ☑ タスクを実行するためにスリープを解除する

### 6. 設定タブ

1. ☑ タスクが失敗した場合の再起動の間隔: `5分`
2. ☑ タスクの再起動の試行回数: `3回`
3. タスクの実行時間の制限: `2時間`
4. OK

## 🧪 テスト実行

### 手動でテスト

PowerShellで:
```powershell
Start-ScheduledTask -TaskName "TikTok_VideoGeneration"
```

または、タスクスケジューラGUIで:
1. タスク一覧から `TikTok_VideoGeneration` を右クリック
2. 「実行する」をクリック

### ログ確認

WSL内で:
```bash
# 実行ログ
tail -f /home/rt/create_short/data/logs/cron/cron_output.log

# 生成ログ
tail -f /home/rt/create_short/data/logs/generation/generation_*.log
```

Windows PowerShellで:
```powershell
# タスク履歴を確認
Get-ScheduledTaskInfo -TaskName "TikTok_VideoGeneration"
```

## 🔍 トラブルシューティング

### タスクが実行されない

1. **WSL2が起動しているか確認**
   ```powershell
   wsl --list --running
   ```

2. **手動実行テスト**
   ```powershell
   wsl -d Ubuntu -u rt -- bash -c "cd /home/rt/create_short && ./scripts/run_daily.sh"
   ```

3. **ログを確認**
   - タスクスケジューラ → タスク履歴
   - `/home/rt/create_short/data/logs/cron/cron_output.log`

### WSL2が自動起動しない

スタートアップに追加:
```powershell
# スタートアップフォルダを開く
shell:startup

# 以下の内容でバッチファイル作成: start_wsl.bat
@echo off
wsl -d Ubuntu -u rt -- echo "WSL started"
```

## 🔄 WSL cronとの併用

両方設定しておくことで冗長性を確保できます:

- **Windowsタスクスケジューラ**: メイン（確実性高い）
- **WSL cron**: バックアップ（Windowsログイン時のみ）

## 🗑️ タスク削除

不要になった場合:
```powershell
Unregister-ScheduledTask -TaskName "TikTok_VideoGeneration" -Confirm:$false
```

## 📊 設定の利点

| 機能 | WSL cron | Windowsタスクスケジューラ |
|------|----------|--------------------------|
| 画面ロック時 | ✅ | ✅ |
| スリープから復帰 | ❌ | ✅ (WakeToRun) |
| ログオフ時 | ❌ | ✅ (S4U) |
| バッテリー駆動 | ✅ | ✅ |
| 失敗時の再試行 | ❌ | ✅ |
| 実行履歴 | 手動確認 | GUI で確認可能 |

## 🚀 次のステップ

1. ✅ タスクスケジューラに登録
2. ✅ テスト実行
3. ✅ ログ確認
4. ⏸️ YouTube API設定（client_secrets.json）
5. ⏸️ 本番運用開始
