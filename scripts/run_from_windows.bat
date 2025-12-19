@echo off
REM Windows タスクスケジューラから実行するバッチファイル
REM 毎日6:00AMに動画生成を実行

echo ================================
echo 日次動画生成開始: %date% %time%
echo ================================

REM WSL経由でスクリプト実行
wsl -d Ubuntu -u rt -- bash -c "cd /home/rt/create_short && ./scripts/run_daily.sh >> data/logs/cron/cron_output.log 2>&1"

echo ================================
echo 完了: %date% %time%
echo ================================
