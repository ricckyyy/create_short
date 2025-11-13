"""
TikTok Selenium - WSL側テストスクリプト（ヘッドレスモード）
Windows側でログイン後、このスクリプトで動作確認
"""

from upload_tiktok_selenium import upload_to_tiktok_selenium
from pathlib import Path
import os

print("=" * 60)
print("TikTok Selenium - テストアップロード（WSL/ヘッドレス）")
print("=" * 60)

# プロファイル確認
profile_path = Path.home() / ".chrome_tiktok_profile"
if not profile_path.exists():
    print("\n❌ エラー: ログインプロファイルが見つかりません")
    print("\n手順:")
    print("1. Windows側で setup_tiktok_login_windows.py を実行")
    print("2. TikTokにログイン")
    print("3. 以下のコマンドでWSLにコピー:")
    print(f"\n   PowerShell/CMD で:")
    print(f"   wsl cp -r '%USERPROFILE%\\.chrome_tiktok_profile' ~/.chrome_tiktok_profile/")
    print("\nまたはWSL内で:")
    print("   cp -r /mnt/c/Users/YourUsername/.chrome_tiktok_profile ~/.chrome_tiktok_profile/")
    exit(1)

print(f"\n✅ プロファイル確認: {profile_path}")

# テスト動画を探す
test_videos = list(Path("data/videos/draft").glob("*.mp4"))
if not test_videos:
    print("\n⚠️ テスト動画が見つかりません")
    print("data/videos/draft/ に動画ファイルを配置してください")
    exit(1)

test_video = test_videos[0]
print(f"\n🎬 テスト動画: {test_video.name}")

# アップロードテスト
print("\n📤 TikTokアップロード開始...")
print("ℹ️ ヘッドレスモードで実行します（ブラウザは表示されません）")

result = upload_to_tiktok_selenium(
    video_path=str(test_video),
    caption="🤖 自動投稿テスト - Selenium版",
    hashtags=["テスト", "自動投稿"],
    headless=True  # ヘッドレスモード
)

print("\n" + "=" * 60)
print("結果:")
print("=" * 60)
print(f"成功: {result.get('success')}")
if result.get('success'):
    print(f"動画: {result.get('video_path')}")
    print(f"キャプション: {result.get('caption')}")
    print("\n✅ アップロード成功！")
else:
    print(f"エラー: {result.get('error')}")
    print("\n❌ アップロード失敗")

print("\n" + "=" * 60)
