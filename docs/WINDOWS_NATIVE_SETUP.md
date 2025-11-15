# Windows ネイティブ環境セットアップガイド

WSLを使わず、Windows上で直接動画生成パイプラインを実行するための手順です。

## 📋 目次

1. [前提条件](#前提条件)
2. [Python環境構築](#python環境構築)
3. [VOICEVOX Engineインストール](#voicevox-engineインストール)
4. [Ollamaインストール](#ollamaインストール)
5. [依存関係インストール](#依存関係インストール)
6. [環境変数設定](#環境変数設定)
7. [タスクスケジューラ設定](#タスクスケジューラ設定)
8. [動作確認](#動作確認)
9. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

- **OS**: Windows 10/11 (64bit)
- **メモリ**: 8GB以上推奨
- **ディスク**: 10GB以上の空き容量
- **ネットワーク**: インターネット接続（初回セットアップ時）

---

## Python環境構築

### 1. Python 3.12のインストール

#### オプションA: 公式インストーラー（推奨）

1. https://www.python.org/downloads/ にアクセス
2. **Python 3.12.x** をダウンロード（最新の3.12系）
3. インストーラー実行時に **"Add Python to PATH"** にチェック ✅
4. "Install Now" をクリック

#### オプションB: winget（Windows Package Manager）

```powershell
winget install Python.Python.3.12
```

### 2. インストール確認

```powershell
python --version
# 出力例: Python 3.12.3

pip --version
# 出力例: pip 24.0 from ...
```

---

## VOICEVOX Engineインストール

### 1. ダウンロード

1. https://github.com/VOICEVOX/voicevox_engine/releases にアクセス
2. 最新版の **`voicevox_engine-windows-cpu-X.X.X.zip`** をダウンロード
   - 例: `voicevox_engine-windows-cpu-0.24.1.zip`

### 2. 解凍

```powershell
# 例: C:\Tools\voicevox_engine に解凍
Expand-Archive -Path "C:\Users\rt\Downloads\voicevox_engine-windows-cpu-0.24.1.zip" -DestinationPath "C:\Tools\"
```

### 3. 起動

```powershell
cd C:\Tools\voicevox_engine
.\run.exe
```

起動後、http://127.0.0.1:50021/docs にアクセスして動作確認

### 4. バックグラウンド起動（推奨）

タスクスケジューラでスタートアップ時に自動起動:

1. タスクスケジューラを開く（`Win + R` → `taskschd.msc`）
2. 「操作」→「基本タスクの作成」
3. トリガー: **Windowsのスタートアップ時**
4. 操作: **プログラムの起動**
   - プログラム: `C:\Tools\voicevox_engine\run.exe`
5. 完了

---

## Ollamaインストール

### 1. インストーラーダウンロード

https://ollama.com/download/windows から **OllamaSetup.exe** をダウンロード

### 2. インストール

1. `OllamaSetup.exe` を実行
2. インストール完了後、自動的にバックグラウンドで起動

### 3. モデルダウンロード

```powershell
ollama pull llama3.2:3b
```

ダウンロード完了まで数分かかります（約2GB）。

### 4. 動作確認

```powershell
ollama list
# 出力に llama3.2:3b が表示されればOK

# テスト実行
ollama run llama3.2:3b "こんにちは"
```

---

## 依存関係インストール

### 1. プロジェクトディレクトリに移動

```powershell
cd C:\Users\rt\create_short
```

### 2. Pythonパッケージインストール

```powershell
pip install moviepy pydub requests pillow
```

### 3. インストール確認

```powershell
python -c "import moviepy; print(moviepy.__version__)"
python -c "from PIL import Image; print('PIL OK')"
```

---

## 環境変数設定

### Pexels APIキー設定

`.env`ファイルをプロジェクトルートに作成:

```powershell
# PowerShellで作成
@"
PEXELS_API_KEY=QqcFiUzxOsDiOYP3sUQyty0hKhTGdzgBQdPQ8nymB7Y1KaXkYocVkctS
OLLAMA_API_URL=http://localhost:11434
VOICEVOX_API_URL=http://127.0.0.1:50021
"@ | Out-File -FilePath .env -Encoding utf8
```

**注意**: 本番環境では独自のAPIキーを取得してください:  
https://www.pexels.com/api/

---

## タスクスケジューラ設定

### 自動設定スクリプト実行

**管理者権限のPowerShell**で実行:

```powershell
cd C:\Users\rt\create_short\scripts
.\setup_windows_task_native.ps1
```

スクリプトが自動的に:
- ✅ Python環境を検出
- ✅ タスク登録（毎日6:00 AM実行）
- ✅ ログディレクトリ作成

### 手動設定（スクリプトが使えない場合）

1. タスクスケジューラを開く（`Win + R` → `taskschd.msc`）
2. 「タスクの作成」をクリック
3. **全般タブ**:
   - 名前: `TikTok_VideoGeneration_Native`
   - 説明: `TikTok/YouTube Shorts用動画自動生成`
4. **トリガータブ**:
   - 新規 → 毎日 6:00 AM
5. **操作タブ**:
   - プログラム: `python`
   - 引数: `C:\Users\rt\create_short\daily_generation.py`
   - 開始: `C:\Users\rt\create_short`
6. **条件タブ**:
   - ☑ コンピューターをAC電源で使用している場合のみ → **チェックを外す**
   - ☑ タスクを実行するためにスリープを解除する → **チェック**
7. OK をクリック

---

## 動作確認

### 1. 手動実行テスト

```powershell
cd C:\Users\rt\create_short
python daily_generation.py
```

正常に動作すれば:
- `data/videos/draft/` に3つの動画ファイルが生成
- `data/logs/generation/` にログが出力

### 2. タスクスケジューラからテスト

1. タスクスケジューラで `TikTok_VideoGeneration_Native` を右クリック
2. 「実行する」を選択
3. `data/logs/cron/cron_output.log` でログ確認

---

## トラブルシューティング

### ❌ `ModuleNotFoundError: No module named 'moviepy'`

**原因**: pip でインストールしたPythonと実行Pythonが異なる

**解決策**:
```powershell
# どのPythonを使っているか確認
where python

# 特定のPythonでインストール
C:\Users\rt\AppData\Local\Programs\Python\Python312\python.exe -m pip install moviepy
```

---

### ❌ VOICEVOX APIに接続できない

**原因**: VOICEVOX Engineが起動していない

**解決策**:
```powershell
# 起動確認
curl http://127.0.0.1:50021/speakers

# 起動していない場合
cd C:\Tools\voicevox_engine
.\run.exe
```

---

### ❌ Ollamaが見つからない

**原因**: Ollamaサービスが起動していない

**解決策**:
```powershell
# サービス確認
Get-Service | Where-Object {$_.Name -like "*ollama*"}

# 手動起動
ollama serve
```

---

### ❌ フォントが見つからない

**原因**: `msgothic.ttc` が存在しない

**解決策**:
```powershell
# フォント確認
Test-Path "C:\Windows\Fonts\msgothic.ttc"

# 存在しない場合、代替フォントを使用
# create_movie.py の font_path を変更:
# font_path = Path("C:/Windows/Fonts/meiryo.ttc")  # メイリオ
```

---

### ❌ タスクスケジューラが実行されない

**原因**: ユーザー権限またはパス設定の問題

**解決策**:

1. タスクのプロパティを開く
2. **全般タブ** → 「ユーザーがログオンしているかどうかにかかわらず実行する」を選択
3. **操作タブ** → プログラムのパスを絶対パスに変更:
   ```
   C:\Users\rt\AppData\Local\Programs\Python\Python312\python.exe
   ```

---

## 次のステップ

1. ✅ 手動実行で動作確認
2. ✅ タスクスケジューラで自動実行確認
3. 📤 YouTube/TikTok自動投稿の設定（別ガイド参照）
4. 📊 analytics.py でパフォーマンス分析

---

## WSL版との違い

| 項目 | WSL版 | Windowsネイティブ版 |
|------|-------|---------------------|
| Python環境 | WSL内のPython | Windows版Python |
| タスクスケジューラ | cron | Windows タスクスケジューラ |
| VOICEVOX | Linux版 | Windows版 |
| Ollama | Linux版 | Windows版 |
| パス形式 | `/home/rt/...` | `C:\Users\rt\...` |
| 起動スクリプト | `run_daily.sh` | `daily_generation.py` 直接実行 |

**パフォーマンス**: ネイティブ版の方がファイルI/Oが高速（約20%改善）

---

## 参考リンク

- [VOICEVOX Engine リリース](https://github.com/VOICEVOX/voicevox_engine/releases)
- [Ollama Windows版](https://ollama.com/download/windows)
- [Python公式サイト](https://www.python.org/)
- [Pexels API](https://www.pexels.com/api/)
