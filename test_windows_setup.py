#!/usr/bin/env python3
"""
Windows環境セットアップ検証スクリプト
全ての依存関係が正しくインストールされているか確認
"""

import sys
import os
from pathlib import Path
import subprocess
import json

def print_header(text):
    """ヘッダー出力"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def check_mark(status):
    """チェックマーク"""
    return "✅" if status else "❌"

def test_python_version():
    """Python バージョン確認"""
    print_header("Python バージョン")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    is_ok = version.major == 3 and version.minor >= 12
    print(f"{check_mark(is_ok)} Python 3.12以上: {is_ok}")
    return is_ok

def test_python_packages():
    """Python パッケージ確認"""
    print_header("Python パッケージ")
    
    packages = {
        "moviepy": "moviepy",
        "PIL": "pillow",
        "requests": "requests",
        "pydub": "pydub",
    }
    
    results = {}
    for import_name, package_name in packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}: インストール済み")
            results[package_name] = True
        except ImportError:
            print(f"❌ {package_name}: 未インストール")
            print(f"   → pip install {package_name}")
            results[package_name] = False
    
    return all(results.values())

def test_voicevox():
    """VOICEVOX Engine 確認"""
    print_header("VOICEVOX Engine")
    
    try:
        import requests
        response = requests.get("http://127.0.0.1:50021/speakers", timeout=3)
        if response.status_code == 200:
            speakers = response.json()
            print(f"✅ VOICEVOX Engine: 起動中")
            print(f"   話者数: {len(speakers)}人")
            return True
        else:
            print(f"❌ VOICEVOX Engine: レスポンスエラー ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ VOICEVOX Engine: 接続できません")
        print(f"   エラー: {e}")
        print(f"   → http://127.0.0.1:50021 で起動してください")
        return False

def test_ollama():
    """Ollama 確認"""
    print_header("Ollama")
    
    try:
        import requests
        # Ollama API確認
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama: 起動中")
            print(f"   インストール済みモデル:")
            for model in models:
                print(f"     - {model.get('name', 'unknown')}")
            
            # llama3.2:3b の確認
            has_llama = any("llama3.2:3b" in m.get("name", "") for m in models)
            if has_llama:
                print(f"   ✅ llama3.2:3b: 利用可能")
            else:
                print(f"   ❌ llama3.2:3b: 未インストール")
                print(f"      → ollama pull llama3.2:3b")
            
            return has_llama
        else:
            print(f"❌ Ollama: レスポンスエラー ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Ollama: 接続できません")
        print(f"   エラー: {e}")
        print(f"   → ollama serve で起動してください")
        return False

def test_font():
    """フォントファイル確認"""
    print_header("フォントファイル")
    
    if os.name == "nt":  # Windows
        font_paths = [
            Path("C:/Windows/Fonts/msgothic.ttc"),
            Path("C:/Windows/Fonts/meiryo.ttc"),
            Path("C:/Windows/Fonts/msmincho.ttc"),
        ]
    else:  # Linux
        font_paths = [
            Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        ]
    
    found = False
    for font_path in font_paths:
        if font_path.exists():
            print(f"✅ フォント: {font_path}")
            found = True
            break
    
    if not found:
        print(f"❌ フォント: 見つかりません")
        print(f"   確認したパス:")
        for font_path in font_paths:
            print(f"     - {font_path}")
    
    return found

def test_project_structure():
    """プロジェクト構造確認"""
    print_header("プロジェクト構造")
    
    project_root = Path(__file__).parent
    
    required_files = [
        "create_movie.py",
        "daily_generation.py",
        "generate_script.py",
        "config.py",
        "db_manager.py",
    ]
    
    required_dirs = [
        "data",
        "docs",
        "scripts",
    ]
    
    all_ok = True
    
    print("必須ファイル:")
    for file in required_files:
        file_path = project_root / file
        exists = file_path.exists()
        print(f"  {check_mark(exists)} {file}")
        all_ok = all_ok and exists
    
    print("\n必須ディレクトリ:")
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        exists = dir_path.exists()
        print(f"  {check_mark(exists)} {dir_name}/")
        all_ok = all_ok and exists
    
    return all_ok

def test_env_file():
    """環境変数ファイル確認"""
    print_header("環境変数ファイル")
    
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        print(f"✅ .env ファイル: 存在します")
        
        # 必須変数の確認
        with open(env_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        required_vars = ["PEXELS_API_KEY"]
        for var in required_vars:
            if var in content:
                print(f"  ✅ {var}: 設定済み")
            else:
                print(f"  ❌ {var}: 未設定")
        
        return True
    else:
        print(f"❌ .env ファイル: 見つかりません")
        print(f"   → .env ファイルを作成してください")
        return False

def test_pexels_api():
    """Pexels API 確認"""
    print_header("Pexels API")
    
    # config.py から API キーを取得
    try:
        from config import PEXELS_API_KEY
        
        if not PEXELS_API_KEY:
            print(f"❌ Pexels API キー: 未設定")
            return False
        
        import requests
        headers = {"Authorization": PEXELS_API_KEY}
        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params={"query": "nature", "per_page": 1},
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Pexels API: 正常動作")
            return True
        elif response.status_code == 401:
            print(f"❌ Pexels API: 認証エラー（APIキーが無効）")
            return False
        else:
            print(f"❌ Pexels API: エラー ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Pexels API: テスト失敗")
        print(f"   エラー: {e}")
        return False

def main():
    """メイン実行"""
    print("\n🔍 Windows環境セットアップ検証")
    print(f"実行環境: {sys.platform}")
    print(f"プロジェクトパス: {Path(__file__).parent}")
    
    results = {
        "Python バージョン": test_python_version(),
        "Python パッケージ": test_python_packages(),
        "VOICEVOX Engine": test_voicevox(),
        "Ollama": test_ollama(),
        "フォント": test_font(),
        "プロジェクト構造": test_project_structure(),
        "環境変数": test_env_file(),
        "Pexels API": test_pexels_api(),
    }
    
    # サマリー
    print_header("検証結果サマリー")
    
    for name, status in results.items():
        print(f"{check_mark(status)} {name}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n合計: {passed}/{total} 項目パス")
    
    if passed == total:
        print("\n🎉 全ての検証に成功しました！")
        print("   daily_generation.py を実行できます。")
        return 0
    else:
        print("\n⚠️  一部の検証に失敗しました。")
        print("   上記のエラーを修正してください。")
        return 1

if __name__ == "__main__":
    exit_code = main()
    
    print("\n" + "=" * 70)
    print("検証完了")
    print("=" * 70)
    
    sys.exit(exit_code)
