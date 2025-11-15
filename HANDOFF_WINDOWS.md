# Windows Copilot 引継ぎドキュメント

**作成日**: 2025-11-15  
**ブランチ**: `feature/windows-native`  
**前環境**: WSL Ubuntu  
**移行先**: Windows ネイティブ

---

## 🎯 引継ぎの目的

WSL環境で開発していたTikTok/YouTube Shorts動画自動生成パイプラインを、**Windowsネイティブ環境で動作させる**ための対応を完了しました。Windows側のCopilotがセットアップ～動作確認を行ってください。

---

## 📦 実装済みの内容

### 1. **タスクスケジューラ自動設定スクリプト**
**ファイル**: `scripts/setup_windows_task_native.ps1`

**機能**:
- WSL経由ではなく、Windows版Pythonを直接実行
- 毎日6:00 AMに `daily_generation.py` を自動実行
- Python環境の自動検出
- ログディレクトリの自動作成
- テスト実行機能付き

**実行方法**:
```powershell
# 管理者権限のPowerShellで実行
cd C:\Users\rt\create_short\scripts
.\setup_windows_task_native.ps1
```

**重要**: スクリプト内の `$ProjectPath` と `$PythonExe` を環境に合わせて調整してください。

---

### 2. **完全セットアップガイド**
**ファイル**: `docs/WINDOWS_NATIVE_SETUP.md`

**内容**:
- Python 3.12インストール手順（公式インストーラー/winget両対応）
- VOICEVOX Engine Windows版のダウンロード～起動
- Ollama Windows版のインストール～モデルダウンロード
- 依存パッケージインストール（moviepy, PIL, requests, pydub）
- 環境変数設定（.env作成）
- タスクスケジューラ設定（自動/手動両方）
- トラブルシューティング6項目

**このドキュメントに従ってセットアップを進めてください。**

---

### 3. **環境検証スクリプト**
**ファイル**: `test_windows_setup.py`

**検証項目** (8項目):
1. ✅ Python 3.12以上
2. ✅ 必須Pythonパッケージ（moviepy, PIL, requests, pydub）
3. ✅ VOICEVOX Engine接続（http://127.0.0.1:50021）
4. ✅ Ollama接続 + llama3.2:3bモデル
5. ✅ フォントファイル（msgothic.ttc等）
6. ✅ プロジェクト構造（必須ファイル/ディレクトリ）
7. ✅ 環境変数ファイル（.env）
8. ✅ Pexels API接続テスト

**実行方法**:
```powershell
cd C:\Users\rt\create_short
python test_windows_setup.py
```

**期待される結果**: `合計: 8/8 項目パス` → 全て成功

---

### 4. **クロスプラットフォーム対応修正**
**ファイル**: `create_movie.py`

**変更内容**:
- フォントパスを `pathlib.Path` で処理
- Windows: `C:/Windows/Fonts/msgothic.ttc`
- Linux: `/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc`
- フォールバック処理追加（Ubuntu以外のLinux対応）

---

## 🚀 実施手順（Windows側で実行）

### ステップ1: プロジェクトフォルダを開く

**方法A: エクスプローラーから**
```
1. エクスプローラーのアドレスバーに貼り付け:
   \\wsl$\Ubuntu\home\rt\create_short

2. フォルダを右クリック → "Codeで開く"
```

**方法B: VS Code Remote - WSL拡張機能**
```
既にWSL環境で開いているので、そのまま作業可能
Windows側から \\wsl$\... でアクセスも可能
```

---

### ステップ2: ブランチ確認

```powershell
git branch
# 出力: * feature/windows-native
```

現在のブランチが `feature/windows-native` であることを確認してください。

---

### ステップ3: 必須ソフトウェアのインストール

#### 3-1. Python 3.12
```powershell
# 公式サイトからダウンロード
https://www.python.org/downloads/

# または winget
winget install Python.Python.3.12

# 確認
python --version
# 期待: Python 3.12.x
```

#### 3-2. VOICEVOX Engine
```powershell
# ダウンロード
https://github.com/VOICEVOX/voicevox_engine/releases

# 最新版の voicevox_engine-windows-cpu-X.X.X.zip をダウンロード
# 例: C:\Tools\voicevox_engine に解凍

# 起動
cd C:\Tools\voicevox_engine
.\run.exe

# ブラウザで確認: http://127.0.0.1:50021/docs
```

#### 3-3. Ollama
```powershell
# ダウンロード
https://ollama.com/download/windows

# インストール後、モデルダウンロード
ollama pull llama3.2:3b

# 確認
ollama list
# 出力に llama3.2:3b があればOK
```

---

### ステップ4: Python依存パッケージインストール

```powershell
cd C:\Users\rt\create_short
pip install moviepy pydub requests pillow
```

**確認**:
```powershell
python -c "import moviepy; print('MoviePy OK')"
python -c "from PIL import Image; print('PIL OK')"
```

---

### ステップ5: 環境変数ファイル作成

`.env` ファイルをプロジェクトルートに作成:

```powershell
# PowerShellで作成
@"
PEXELS_API_KEY=QqcFiUzxOsDiOYP3sUQyty0hKhTGdzgBQdPQ8nymB7Y1KaXkYocVkctS
OLLAMA_API_URL=http://localhost:11434
VOICEVOX_API_URL=http://127.0.0.1:50021
"@ | Out-File -FilePath .env -Encoding utf8
```

---

### ステップ6: 環境検証スクリプト実行

```powershell
python test_windows_setup.py
```

**期待される出力**:
```
✅ Python バージョン
✅ Python パッケージ
✅ VOICEVOX Engine
✅ Ollama
✅ フォント
✅ プロジェクト構造
✅ 環境変数
✅ Pexels API

合計: 8/8 項目パス
🎉 全ての検証に成功しました！
```

**失敗した場合**: 各項目のエラーメッセージに従って修正してください。

---

### ステップ7: 手動テスト実行

```powershell
cd C:\Users\rt\create_short
python daily_generation.py
```

**期待される結果**:
- `data/videos/draft/` に3つの動画ファイル生成
  - `psychology_shinrigaku_YYYYMMDD.mp4`
  - `horror_kowai_YYYYMMDD.mp4`
  - `cinema_movie_YYYYMMDD.mp4`
- `data/logs/generation/` にログ出力
- エラーなく完了

---

### ステップ8: タスクスケジューラ設定

**自動設定（推奨）**:
```powershell
# 管理者権限のPowerShellで実行
cd C:\Users\rt\create_short\scripts
.\setup_windows_task_native.ps1
```

スクリプトが自動的に:
- Python環境を検出
- タスク `TikTok_VideoGeneration_Native` を作成
- 毎日6:00 AM実行に設定

**手動設定**:
`docs/WINDOWS_NATIVE_SETUP.md` の「手動設定」セクション参照

---

### ステップ9: タスクスケジューラからテスト実行

1. タスクスケジューラを開く: `Win + R` → `taskschd.msc`
2. `TikTok_VideoGeneration_Native` を検索
3. 右クリック → 「実行する」
4. `data/logs/cron/cron_output.log` でログ確認

---

## 📊 検証チェックリスト

Windows側のCopilotは以下を確認してください:

- [ ] Python 3.12がインストール済み（`python --version`）
- [ ] VOICEVOX Engineが起動中（http://127.0.0.1:50021/docs にアクセス可能）
- [ ] Ollamaが起動中（`ollama list` でllama3.2:3b表示）
- [ ] Python依存パッケージインストール済み（`pip list | grep moviepy`）
- [ ] .envファイルが存在（`Test-Path .env` → True）
- [ ] `test_windows_setup.py` が8/8項目パス
- [ ] `daily_generation.py` が手動実行で成功
- [ ] タスクスケジューラから実行成功
- [ ] 生成された動画が再生可能（VLCなどで確認）

---

## 🐛 よくあるトラブルと解決策

### ❌ `ModuleNotFoundError: No module named 'moviepy'`

**原因**: pipでインストールしたPythonと実行Pythonが異なる

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
cd C:\Tools\voicevox_engine
.\run.exe
```

---

### ❌ Ollamaが見つからない

**原因**: Ollamaサービスが起動していない

**解決策**:
```powershell
ollama serve
```

---

### ❌ フォントが見つからない

**原因**: msgothic.ttc が存在しない

**解決策**:
```powershell
# 代替フォントを使用（create_movie.py を編集）
# font_path = Path("C:/Windows/Fonts/meiryo.ttc")  # メイリオ
```

---

## 📁 ファイル構造（重要なファイル）

```
C:\Users\rt\create_short\
├── daily_generation.py          ← メインスクリプト（毎日実行）
├── create_movie.py              ← 動画生成ロジック
├── generate_script.py           ← 台本生成（Ollama利用）
├── test_windows_setup.py        ← 環境検証スクリプト（実行推奨）
├── config.py                    ← 設定ファイル
├── .env                         ← 環境変数（作成必要）
├── docs/
│   └── WINDOWS_NATIVE_SETUP.md  ← 完全セットアップガイド
└── scripts/
    └── setup_windows_task_native.ps1  ← タスクスケジューラ自動設定
```

---

## 🔄 次のステップ（Windows側で実施）

1. ✅ 上記手順に従ってセットアップ
2. ✅ `test_windows_setup.py` で全項目パス確認
3. ✅ `daily_generation.py` 手動実行成功
4. ✅ タスクスケジューラ設定完了
5. 📝 動作確認結果をコミット:
   ```powershell
   git add .
   git commit -m "test: Windows環境での動作確認完了"
   ```
6. 🔀 developブランチにマージ:
   ```powershell
   git checkout develop
   git merge feature/windows-native
   git push origin develop
   ```

---

## 📞 サポート情報

**参考ドキュメント**:
- `docs/WINDOWS_NATIVE_SETUP.md` - 完全セットアップガイド
- `.github/copilot-instructions.md` - プロジェクト全体の指示

**トラブル時**:
- `test_windows_setup.py` のエラーメッセージを確認
- `docs/WINDOWS_NATIVE_SETUP.md` のトラブルシューティングセクション参照

---

## 🎉 完了条件

以下が全て達成されたら、Windows移行完了です:

- [ ] `test_windows_setup.py` が 8/8 項目パス
- [ ] `daily_generation.py` が手動実行で3動画生成成功
- [ ] タスクスケジューラから自動実行成功
- [ ] 生成された動画が正常に再生可能
- [ ] ログファイルにエラーなし

**完了後**: developブランチにマージして、WSL環境との並行運用またはWindows完全移行を判断してください。

---

**引継ぎ元**: WSL Ubuntu (rt@DESKTOP-F8EFI7M)  
**引継ぎ先**: Windows 11 Copilot  
**コミット**: `910327c` (feat: Windows ネイティブ環境対応)
