# 📁 フォルダ構造ガイド

## 新しいディレクトリ構造（2025年11月8日更新）

プロジェクトは整理された階層構造に変更されました。全てのデータは `data/` ディレクトリ配下に格納されます。

```
create_short/
├── config.py                    # 設定・パス管理（全てのパスを一元管理）
├── migrate.py                   # 旧構造から新構造への移行スクリプト
│
├── data/                        # === データディレクトリ（全ての生成物） ===
│   ├── videos/                  # 動画ファイル
│   │   ├── draft/              # 下書き・生成直後の動画
│   │   └── published/          # 投稿済み動画
│   │
│   ├── audio/                  # 一時音声ファイル（自動削除）
│   │
│   ├── scripts/                # 台本管理
│   │   ├── history/           # 生成された台本の履歴
│   │   └── archive/           # アーカイブ（古い台本）
│   │
│   ├── logs/                   # ログファイル
│   │   ├── generation/        # 動画生成ログ
│   │   ├── upload/            # 投稿ログ（今後実装）
│   │   └── cron/              # cron実行ログ
│   │
│   ├── assets/                 # ダウンロード素材
│   │   └── video_clips/       # Pexelsからの動画クリップ（自動削除）
│   │
│   └── upload/                 # 投稿管理（今後実装）
│       ├── queue/             # 投稿待ちキュー
│       └── history/           # 投稿履歴
│
├── app.py                      # Webアプリ
├── create_movie.py             # 動画生成コア
├── generate_script.py          # AI台本生成
├── daily_generation.py         # 日次自動生成
│
└── templates/                  # Webアプリテンプレート
    └── index.html
```

## 主要ディレクトリの説明

### 📹 `data/videos/`
生成された動画ファイルを管理

- **`draft/`**: 生成直後の動画（投稿前）
- **`published/`**: 投稿済みの動画

**命名規則**: `{prefix}_{slug}_{YYYYMMDD}.mp4`
- 例: `psychology_shinrigaku_20251108.mp4`
- 例: `horror_kowai_20251108.mp4`

### 📝 `data/scripts/`
台本とその履歴を管理

- **`history/`**: 生成された台本ファイル
  - テキストファイル: `script_{slug}_{YYYYMMDD}_{HHMMSS}.txt`
  - JSONデータ: `scripts_{YYYYMMDD}.json`
- **`archive/`**: 古い台本のアーカイブ

### 📊 `data/logs/`
各種ログを分類して保存

- **`generation/`**: 動画生成プロセスのログ
  - `generation_{YYYYMMDD}.log`
- **`upload/`**: 投稿処理のログ（今後実装）
- **`cron/`**: cron実行のログ

### 🎵 `data/audio/`
一時的な音声ファイル（VOICEVOX生成）

- 動画生成後に自動削除
- 命名: `voice_{slug}_{YYYYMMDD}.wav`

### 🎬 `data/assets/video_clips/`
Pexelsからダウンロードした動画素材

- 動画生成後に自動削除
- 命名: `clip_{番号}_{プロセスID}.mp4`

## 設定管理（`config.py`）

全てのパスとディレクトリ構造は `config.py` で一元管理されています。

### 主要な関数

```python
from config import (
    init_directories,        # ディレクトリ構造を初期化
    get_video_path,         # 動画ファイルパスを取得
    get_audio_path,         # 音声ファイルパスを取得
    get_script_path,        # 台本ファイルパスを取得
    cleanup_temp_files,     # 一時ファイルを削除
)
```

### アカウント設定

```python
ACCOUNTS = {
    "心理テストラボ": {
        "slug": "shinrigaku",
        "voice_speaker": 1,      # ずんだもん
        "voice_pitch": 0,
        "video_prefix": "psychology"
    },
    # ... 他のアカウント
}
```

## 旧構造からの移行

既存プロジェクトの場合、以下のコマンドで自動移行：

```bash
python migrate.py
```

このスクリプトは：
1. `output/` → `data/videos/draft/` に動画を移動
2. `script_history/` → `data/scripts/history/` に台本を移動
3. `logs/` → `data/logs/generation/` にログを移動
4. 一時ファイル（`.wav`, `clip*.mp4`）を削除
5. 古いディレクトリを削除（確認後）

## メンテナンス

### ディスク容量の管理

```bash
# 30日以上古い下書き動画を削除
find data/videos/draft -name "*.mp4" -mtime +30 -delete

# アーカイブに移動してから削除
find data/scripts/history -name "*.txt" -mtime +90 -exec mv {} data/scripts/archive/ \;
```

### ログローテーション

```bash
# 60日以上古いログを削除
find data/logs -name "*.log" -mtime +60 -delete
```

## よくある質問

### Q: 古い`output/`ディレクトリのファイルはどうなる？
A: `migrate.py`を実行すると自動的に`data/videos/draft/`に移動されます。

### Q: 一時ファイルはいつ削除される？
A: 動画生成完了後、`cleanup_temp_files()`が自動実行され、`audio/`と`assets/video_clips/`がクリーンアップされます。

### Q: 手動でディレクトリを作成する必要は？
A: いいえ。全てのスクリプトが`init_directories()`を呼び出し、必要なディレクトリを自動作成します。

### Q: パスを変更したい場合は？
A: `config.py`の該当変数を編集してください。全スクリプトが自動的に新しいパスを使用します。

---

**この新構造により、ファイル管理が整理され、自動投稿機能の実装準備も完了しました！**
