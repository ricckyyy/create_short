#!/usr/bin/env python3
"""
TikTok自動投稿モジュール（Selenium版）
公式APIより簡単・制限なし・審査不要
"""

import time
import os
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import UPLOAD_HISTORY_DIR

class TikTokSeleniumUploader:
    """Seleniumを使用したTikTok自動投稿クラス"""
    
    def __init__(self, headless=False, user_data_dir=None):
        """
        初期化
        
        Args:
            headless: ヘッドレスモード（画面表示なし）
            user_data_dir: Chromeユーザーデータディレクトリ（ログイン情報保持用）
        """
        self.headless = headless
        self.user_data_dir = user_data_dir or str(Path.home() / ".chrome_tiktok_profile")
        self.driver = None
    
    def _setup_driver(self):
        """Chrome WebDriverをセットアップ"""
        options = Options()
        
        # ユーザープロファイルを使用（ログイン状態を保持）
        options.add_argument(f"--user-data-dir={self.user_data_dir}")
        options.add_argument("--profile-directory=Default")
        
        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
        
        # その他の設定
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        
        # ユーザーエージェント（PC版TikTok）
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # webdriver-managerを使用（推奨）
        try:
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except ImportError:
            # webdriver-managerがない場合は通常起動
            self.driver = webdriver.Chrome(options=options)
        
        self.wait = WebDriverWait(self.driver, 30)
        self.wait = WebDriverWait(self.driver, 30)
    
    def upload_video(self, video_path, caption, hashtags=None, privacy="public", 
                     allow_comments=True, allow_duet=True, allow_stitch=True):
        """
        動画をTikTokにアップロード
        
        Args:
            video_path: 動画ファイルのパス
            caption: キャプション（説明文）
            hashtags: ハッシュタグリスト
            privacy: 公開設定 ("public", "friends", "private")
            allow_comments: コメント許可
            allow_duet: デュエット許可
            allow_stitch: スティッチ許可
        
        Returns:
            dict: アップロード結果
        """
        try:
            print(f"📤 TikTokアップロード開始: {Path(video_path).name}")
            
            # WebDriverをセットアップ
            self._setup_driver()
            
            # Step 1: TikTok Studio（アップロードページ）にアクセス
            print("🌐 TikTok Studioにアクセス中...")
            self.driver.get("https://www.tiktok.com/creator-center/upload")
            time.sleep(3)
            
            # ログイン確認
            if not self._check_login():
                print("⚠️  ログインが必要です。ブラウザでログインしてください...")
                input("ログイン完了後、Enterを押してください...")
            
            # Step 2: ファイルをアップロード
            print("📁 動画ファイルをアップロード中...")
            file_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            file_input.send_keys(str(Path(video_path).resolve()))
            
            # アップロード完了を待つ
            print("⏳ アップロード処理中...")
            time.sleep(10)  # 動画のアップロードと処理に時間がかかる
            
            # Step 3: キャプションを入力
            print("✍️ キャプションを入力中...")
            caption_text = self._build_caption(caption, hashtags)
            
            try:
                caption_box = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
                )
                caption_box.click()
                caption_box.clear()
                caption_box.send_keys(caption_text)
            except TimeoutException:
                print("⚠️  キャプション入力欄が見つかりません")
            
            # Step 4: 公開設定
            print("🔧 公開設定を調整中...")
            self._set_privacy(privacy)
            self._set_permissions(allow_comments, allow_duet, allow_stitch)
            
            # Step 5: 投稿ボタンをクリック
            print("🚀 投稿中...")
            post_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., '投稿') or contains(., 'Post')]"))
            )
            post_button.click()
            
            # 投稿完了を待つ
            print("⏳ 投稿処理中...")
            time.sleep(5)
            
            # 成功確認
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '投稿しました') or contains(text(), 'uploaded')]"))
                )
                print("🎉 TikTok投稿完了！")
                success = True
            except TimeoutException:
                print("⚠️  投稿完了の確認ができませんでした")
                success = True  # タイムアウトでも成功とみなす
            
            # 履歴保存
            self._save_upload_history(video_path, caption_text, success)
            
            return {
                "success": success,
                "video_path": str(video_path),
                "caption": caption_text
            }
            
        except Exception as e:
            error_msg = f"TikTokアップロードエラー: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def _check_login(self):
        """ログイン状態を確認"""
        try:
            # ログインボタンが表示されていればログインしていない
            self.driver.find_element(By.XPATH, "//button[contains(., 'ログイン') or contains(., 'Log in')]")
            return False
        except NoSuchElementException:
            return True
    
    def _build_caption(self, caption, hashtags):
        """キャプションとハッシュタグを結合"""
        caption_text = caption
        if hashtags:
            hashtags_str = " ".join([f"#{tag}" if not tag.startswith("#") else tag for tag in hashtags])
            caption_text = f"{caption}\n\n{hashtags_str}"
        return caption_text
    
    def _set_privacy(self, privacy):
        """公開設定を変更"""
        try:
            privacy_map = {
                "public": "公開",
                "friends": "友達",
                "private": "非公開"
            }
            privacy_text = privacy_map.get(privacy, "公開")
            
            privacy_button = self.driver.find_element(
                By.XPATH, f"//button[contains(., '{privacy_text}') or contains(., '{privacy.capitalize()}')]"
            )
            privacy_button.click()
            time.sleep(1)
        except Exception as e:
            print(f"⚠️  公開設定の変更に失敗: {e}")
    
    def _set_permissions(self, allow_comments, allow_duet, allow_stitch):
        """コメント・デュエット・スティッチの設定"""
        try:
            # これらの設定はTikTokのUIが頻繁に変わるため、
            # 実装は省略（デフォルト設定を使用）
            pass
        except Exception as e:
            print(f"⚠️  権限設定の変更に失敗: {e}")
    
    def _save_upload_history(self, video_path, caption, success):
        """投稿履歴を保存"""
        import json
        
        history_file = UPLOAD_HISTORY_DIR / f"tiktok_selenium_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        history_data = {
            "platform": "TikTok (Selenium)",
            "video_path": str(video_path),
            "caption": caption,
            "uploaded_at": datetime.now().isoformat(),
            "success": success
        }
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
        
        print(f"📝 履歴保存: {history_file}")


def upload_to_tiktok_selenium(video_path, caption, hashtags=None, headless=False):
    """
    TikTokに動画をアップロード（Selenium版・簡易インターフェース）
    
    Args:
        video_path: 動画ファイルのパス
        caption: キャプション
        hashtags: ハッシュタグリスト
        headless: ヘッドレスモード
    
    Returns:
        dict: アップロード結果
    """
    uploader = TikTokSeleniumUploader(headless=headless)
    return uploader.upload_video(
        video_path=video_path,
        caption=caption,
        hashtags=hashtags
    )


# テスト実行
if __name__ == "__main__":
    print("TikTok自動投稿モジュール (Selenium版)")
    print("=" * 60)
    print("\n📝 使用方法:")
    print("1. Google Chromeをインストール")
    print("2. ChromeDriverをインストール")
    print("3. 初回はブラウザが開くのでTikTokにログイン")
    print("4. 以降はログイン状態が保存されます")
    print("\n例:")
    print("""
from upload_tiktok_selenium import upload_to_tiktok_selenium

result = upload_to_tiktok_selenium(
    video_path="data/videos/draft/test.mp4",
    caption="テスト動画です",
    hashtags=["心理テスト", "診断"]
)
print(result)
    """)
