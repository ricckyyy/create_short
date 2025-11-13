# TikTok Selenium - Windows→WSL セットアップガイド

## 🎯 手順の流れ

```
Windows側でログイン → プロファイルをWSLにコピー → WSLでヘッドレス実行
```

---

## 📋 ステップ1: Windows側で初回ログイン

### 1-1. 必要なパッケージをインストール

**WindowsのコマンドプロンプトまたはPowerShell:**

```powershell
pip install selenium webdriver-manager
```

### 1-2. ログインスクリプトを実行

```powershell
# Windows側で実行
python setup_tiktok_login_windows.py
```

### 1-3. ブラウザでログイン

1. Chromeブラウザが自動で開きます
2. TikTokにログイン（メール/電話番号/SNS連携）
3. ログイン完了後、ターミナルに戻って**Enterキー**を押す
4. ログイン情報が `C:\Users\YourUsername\.chrome_tiktok_profile\` に保存される

---

## 📋 ステップ2: WSLにプロファイルをコピー

### 方法A: Windowsから直接コピー（推奨）

**PowerShellまたはコマンドプロンプト:**

```powershell
# プロファイルをWSLにコピー
wsl cp -r "$env:USERPROFILE\.chrome_tiktok_profile" ~/.chrome_tiktok_profile/
```

### 方法B: WSL内でWindowsのファイルシステムからコピー

**WSLターミナル:**

```bash
# Windowsのユーザー名を確認
echo $USER  # WSLのユーザー名
ls /mnt/c/Users/  # Windowsのユーザー一覧

# コピー（YourUsernameを実際の名前に変更）
cp -r /mnt/c/Users/YourUsername/.chrome_tiktok_profile ~/.chrome_tiktok_profile/

# 確認
ls -la ~/.chrome_tiktok_profile/
```

---

## 📋 ステップ3: WSLで動作確認

### 3-1. 必要なパッケージをインストール（WSL側）

```bash
# WSLのPythonにインストール
pip install selenium webdriver-manager
```

### 3-2. テストスクリプトを実行

```bash
# WSL側で実行（ヘッドレスモード）
python test_tiktok_upload.py
```

### 3-3. 成功メッセージを確認

```
✅ プロファイル確認: /home/username/.chrome_tiktok_profile
🎬 テスト動画: shinrigaku.mp4
📤 TikTokアップロード開始...
✅ アップロード成功！
```

---

## 🐛 トラブルシューティング

### 問題1: プロファイルが見つからない

```bash
# WSL側で確認
ls -la ~/.chrome_tiktok_profile/

# なければコピーし直す
cp -r /mnt/c/Users/YourUsername/.chrome_tiktok_profile ~/.chrome_tiktok_profile/
```

### 問題2: Windowsのユーザー名がわからない

**Windows側:**
```powershell
echo %USERNAME%
```

**WSL側:**
```bash
ls /mnt/c/Users/
```

### 問題3: ChromeDriverのエラー

```bash
# WSL側でChromeをインストール
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# ChromeDriverは自動インストール（webdriver-manager使用）
```

### 問題4: ログインが保持されない

Windows側でもう一度ログイン：

```powershell
python setup_tiktok_login_windows.py
```

---

## 🎬 daily_generation.pyに統合

WSLで動作確認できたら、自動投稿に統合：

```python
# daily_generation.py の最後に追加

from upload_tiktok_selenium import upload_to_tiktok_selenium

def upload_videos_to_tiktok():
    """生成した動画をTikTokに投稿"""
    for account in accounts:
        print(f"\n📤 TikTok投稿: {account['name']}")
        
        result = upload_to_tiktok_selenium(
            video_path=account['output'],
            caption=account['script'].split('\n')[0],  # 最初の行をキャプション
            hashtags=account.get('hashtags', []),
            headless=True  # WSLではヘッドレスモード
        )
        
        if result['success']:
            print(f"✅ {account['name']} 投稿完了")
        else:
            print(f"❌ {account['name']} 投稿失敗: {result.get('error')}")

# 動画生成後に実行
if __name__ == "__main__":
    generate_all_videos()
    upload_videos_to_tiktok()
```

---

## 📊 ファイル構成

```
create_short/
├── setup_tiktok_login_windows.py   # Windows側: 初回ログイン用
├── test_tiktok_upload.py           # WSL側: 動作確認用
├── upload_tiktok_selenium.py       # 本体
└── docs/
    └── WINDOWS_WSL_SETUP.md        # このファイル
```

---

## ✅ チェックリスト

- [ ] Windows側で `setup_tiktok_login_windows.py` 実行
- [ ] TikTokにログイン完了
- [ ] プロファイルがWSLにコピーされた
- [ ] WSL側で `test_tiktok_upload.py` が成功
- [ ] `daily_generation.py` に統合完了

---

## 💡 Tips

### 複数アカウント対応

アカウントごとにプロファイルを分ける：

**Windows側:**
```powershell
# アカウントA用
python setup_tiktok_login_windows.py
# ログイン後、リネーム
Rename-Item "$env:USERPROFILE\.chrome_tiktok_profile" ".chrome_tiktok_account_a"

# アカウントB用
python setup_tiktok_login_windows.py
Rename-Item "$env:USERPROFILE\.chrome_tiktok_profile" ".chrome_tiktok_account_b"
```

**WSL側:**
```bash
# コピー
cp -r /mnt/c/Users/YourUsername/.chrome_tiktok_account_a ~/.chrome_tiktok_account_a/
cp -r /mnt/c/Users/YourUsername/.chrome_tiktok_account_b ~/.chrome_tiktok_account_b/

# 使い分け
uploader_a = TikTokSeleniumUploader(user_data_dir="~/.chrome_tiktok_account_a")
uploader_b = TikTokSeleniumUploader(user_data_dir="~/.chrome_tiktok_account_b")
```

---

**作成日**: 2025-01-12  
**対象**: Windows + WSL環境でのTikTok自動投稿
