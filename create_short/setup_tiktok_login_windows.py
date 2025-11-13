"""
TikTok Selenium - Windows側での初回ログインスクリプト
実行後、プロファイルをWSLにコピーしてください
"""

from upload_tiktok_selenium import TikTokSeleniumUploader
from pathlib import Path
import os

print("=" * 60)
print("TikTok Selenium - 初回ログイン（Windows用）")
print("=" * 60)

# Windows用のプロファイルパス
windows_profile = str(Path.home() / ".chrome_tiktok_profile")
print(f"\n📁 プロファイル保存先: {windows_profile}")

# ブラウザを表示してログイン
print("\n🌐 ブラウザを起動します...")
print("📝 手順:")
print("  1. TikTokにログイン")
print("  2. ログイン完了を確認")
print("  3. このウィンドウに戻ってEnterキーを押す")

uploader = TikTokSeleniumUploader(headless=False)

try:
    # TikTok Studioにアクセス
    uploader._setup_driver()
    print("\n🌐 TikTok Studioにアクセス中...")
    uploader.driver.get("https://www.tiktok.com/creator-center/upload")
    
    # ログイン待機
    print("\n⏳ ブラウザでTikTokにログインしてください...")
    input("\n✅ ログイン完了後、Enterキーを押してください: ")
    
    # ログイン確認
    if uploader._check_login():
        print("\n✅ ログイン成功！")
        print(f"📁 ログイン情報が保存されました: {windows_profile}")
        print("\n" + "=" * 60)
        print("次のステップ:")
        print("=" * 60)
        print("\n1. PowerShellまたはコマンドプロンプトを開く")
        print("2. 以下のコマンドを実行してWSLにコピー:")
        print(f"\n   wsl cp -r '{windows_profile}' ~/.chrome_tiktok_profile/")
        print("\n3. WSL側でヘッドレスモードで実行:")
        print("   python test_tiktok_upload.py")
        print("\n" + "=" * 60)
    else:
        print("\n❌ ログインが確認できませんでした")
        print("もう一度やり直してください")

except Exception as e:
    print(f"\n❌ エラー: {e}")

finally:
    if uploader.driver:
        print("\n🔄 ブラウザを閉じています...")
        uploader.driver.quit()

print("\n完了！")
