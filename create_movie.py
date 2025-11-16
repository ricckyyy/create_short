# --- 必要ライブラリ ---
# pip install moviepy pydub requests

import os
from pathlib import Path
from config import init_directories, ASSETS_VIDEO_DIR

# ディレクトリ初期化
init_directories()

import requests
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip, ColorClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import shutil

# VOICEVOX Engine API
VOICEVOX_API = "http://127.0.0.1:50021"

# -------------------------
# 字幕画像作成（白文字＋黒縁）
# -------------------------
def create_subtitle_image(text, width=720, height=200, fontsize=30):
    # クロスプラットフォーム対応のフォントパス
    if os.name == "nt":  # Windows
        font_path = Path("C:/Windows/Fonts/msgothic.ttc")
    else:  # Linux/Unix
        font_path = Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc")
        if not font_path.exists():
            # Ubuntu以外のLinux向けフォールバック
            font_path = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
    
    font = ImageFont.truetype(str(font_path), fontsize)
    img = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)

    # 20文字ごとに改行
    lines = [text[i:i+20] for i in range(0, len(text), 20)]
    y = (height - len(lines)*(fontsize+10))//2

    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font)
        w = bbox[2]-bbox[0]
        x = (width-w)//2

        # 黒い縁取りを描画
        for dx in [-2,-1,0,1,2]:
            for dy in [-2,-1,0,1,2]:
                if dx != 0 or dy != 0:
                    draw.text((x+dx, y+dy), line, font=font, fill="black")

        # 白文字を上に描画
        draw.text((x, y), line, font=font, fill="white")
        y += fontsize + 10

    return np.array(img)

# -------------------------
# VOICEVOX: 話者リスト取得
# -------------------------
def get_speakers():
    url = f"{VOICEVOX_API}/speakers"
    res = requests.get(url)
    res.raise_for_status()
    return res.json()

# -------------------------
# VOICEVOX: 音声生成
# -------------------------
def generate_voice(text, speaker_index=0, style_index=0, pitch=-0.5, speed=1.0, filename="voice.wav"):
    print(f"🎤 音声生成開始: {filename}")
    print(f"   テキスト長: {len(text)} 文字")
    
    try:
        speakers = get_speakers()
        if speaker_index >= len(speakers):
            raise ValueError(f"speaker_index {speaker_index} は範囲外です")

        speaker = speakers[speaker_index]
        speaker_name = speaker["name"]
        
        if style_index >= len(speaker["styles"]):
            style_index = 0
        style_id = speaker["styles"][style_index]["id"]
        
        print(f"   話者: {speaker_name} (ID:{style_id})")

        # audio_query
        print(f"   ステップ1: audio_query生成中...")
        url_query = f"{VOICEVOX_API}/audio_query"
        res = requests.post(url_query, params={"text": text, "speaker": style_id}, timeout=10)
        res.raise_for_status()
        audio_query = res.json()
        print(f"   ✅ audio_query生成完了")

        # ピッチ・速度調整
        audio_query["speedScale"] = speed
        audio_query["pitchScale"] = pitch

        # synthesis
        print(f"   ステップ2: 音声合成中...")
        url_speech = f"{VOICEVOX_API}/synthesis?speaker={style_id}"
        res2 = requests.post(url_speech, json=audio_query, timeout=60)
        res2.raise_for_status()
        
        with open(filename, "wb") as f:
            f.write(res2.content)
        
        file_size = len(res2.content)
        print(f"✅ 音声生成完了: {filename} ({file_size/1024:.1f} KB)")
        print(f"   話者: {speaker_name} / style={speaker['styles'][style_index]['name']}")
        return filename
        
    except Exception as e:
        print(f"❌ 音声生成エラー: {e}")
        import traceback
        traceback.print_exc()
        raise

# -------------------------
# Pexels: 動画検索
# -------------------------
def search_pexels_video(query, api_key, max_results=15, max_retries=3):
    import time
    import random
    print(f"  🔍 Pexels検索: '{query}'")
    headers = {"Authorization": api_key}
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait_time = 2 ** attempt  # exponential backoff: 2秒, 4秒, 8秒
                print(f"     ⏳ リトライ {attempt + 1}/{max_retries} - {wait_time}秒待機...")
                time.sleep(wait_time)
            
            print(f"     📡 API接続中... (試行 {attempt + 1}/{max_retries})")
            r = requests.get(
                "https://api.pexels.com/videos/search", 
                headers=headers, 
                params={"query": query, "per_page": max_results}, 
                timeout=30
            )
            r.raise_for_status()
            vs = r.json().get("videos", [])
            
            if not vs:
                print(f"     ⚠️ 検索結果なし: '{query}'")
                return []
            
            print(f"     📦 {len(vs)}件の候補から選択中...")
            
            # ランダムに1つ選択して多様性を確保
            selected_video = random.choice(vs)
            
            if selected_video.get("video_files"):
                # SD品質を優先、なければHD 720p、最後の手段でそれ以外
                video_files = selected_video["video_files"]
                sd_files = [f for f in video_files if f.get("quality") == "sd"]
                hd_files = [f for f in video_files if f.get("quality") == "hd" and f.get("width", 0) <= 1280]
                
                selected_file = None
                if sd_files:
                    selected_file = sd_files[0]
                    print(f"     ✅ SD動画を選択 ({selected_file.get('width')}x{selected_file.get('height')})")
                elif hd_files:
                    selected_file = hd_files[0]
                    print(f"     ✅ HD動画を選択 ({selected_file.get('width')}x{selected_file.get('height')})")
                else:
                    selected_file = video_files[0]
                    print(f"     ✅ 動画を選択 ({selected_file.get('quality')})")
                
                if selected_file:
                    return [selected_file["link"]]
            
            print(f"     ⚠️ 有効な動画ファイルが見つかりませんでした")
            return []
            
        except requests.exceptions.Timeout as e:
            print(f"     ⏱️ タイムアウト発生 (試行 {attempt + 1}/{max_retries})")
            print(f"        エラー詳細: {type(e).__name__}: {e}")
            if attempt == max_retries - 1:
                print(f"     ❌ 最大リトライ回数に到達。検索失敗: '{query}'")
                import traceback
                traceback.print_exc()
                return []
                
        except requests.exceptions.ConnectionError as e:
            print(f"     🔌 接続エラー発生 (試行 {attempt + 1}/{max_retries})")
            print(f"        エラー詳細: {type(e).__name__}: {e}")
            if attempt == max_retries - 1:
                print(f"     ❌ 最大リトライ回数に到達。接続失敗: '{query}'")
                import traceback
                traceback.print_exc()
                return []
                
        except requests.exceptions.HTTPError as e:
            status_code = r.status_code if 'r' in locals() else 'N/A'
            print(f"     🚫 HTTPエラー (ステータスコード: {status_code})")
            print(f"        エラー詳細: {type(e).__name__}: {e}")
            print(f"     ❌ APIエラー。リトライしません: '{query}'")
            import traceback
            traceback.print_exc()
            return []
            
        except KeyboardInterrupt:
            print(f"\n     ⚠️ ユーザーによる中断検出")
            raise
            
        except Exception as e:
            print(f"     ❌ 予期しないエラー (試行 {attempt + 1}/{max_retries})")
            print(f"        エラータイプ: {type(e).__name__}")
            print(f"        エラー詳細: {e}")
            if attempt == max_retries - 1:
                print(f"     ❌ 最大リトライ回数に到達。検索失敗: '{query}'")
                import traceback
                traceback.print_exc()
                return []
    
    return []

# -------------------------
# 動画ダウンロード
# -------------------------
def download_video(url, filename, max_retries=3):
    import time
    if not url:
        print(f"     ⚠️ URLなし、ダウンロードスキップ")
        return None
    
    print(f"  📥 ダウンロード: {filename}")
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait_time = 2 ** attempt
                print(f"     ⏳ リトライ {attempt + 1}/{max_retries} - {wait_time}秒待機...")
                time.sleep(wait_time)
            
            print(f"     📡 接続中... (試行 {attempt + 1}/{max_retries})")
            r = requests.get(url, stream=True, timeout=300)  # 5分（大きな動画対応）
            r.raise_for_status()
            
            total_size = int(r.headers.get('content-length', 0))
            print(f"     📦 ファイルサイズ: {total_size/1024/1024:.2f} MB")
            
            downloaded = 0
            with open(filename, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r     ⏬ 進捗: {percent:.1f}%", end="", flush=True)
            
            print(f"\n     ✅ ダウンロード完了: {downloaded/1024/1024:.2f} MB")
            return filename
            
        except requests.exceptions.Timeout as e:
            print(f"\n     ⏱️ ダウンロードタイムアウト (試行 {attempt + 1}/{max_retries})")
            print(f"        エラー詳細: {type(e).__name__}: {e}")
            if attempt == max_retries - 1:
                print(f"     ❌ 最大リトライ回数に到達。ダウンロード失敗")
                import traceback
                traceback.print_exc()
                return None
                
        except requests.exceptions.ConnectionError as e:
            print(f"\n     🔌 接続エラー発生 (試行 {attempt + 1}/{max_retries})")
            print(f"        エラー詳細: {type(e).__name__}: {e}")
            if attempt == max_retries - 1:
                print(f"     ❌ 最大リトライ回数に到達。接続失敗")
                import traceback
                traceback.print_exc()
                return None
                
        except requests.exceptions.HTTPError as e:
            status_code = r.status_code if 'r' in locals() else 'N/A'
            print(f"\n     🚫 HTTPエラー (ステータスコード: {status_code})")
            print(f"        エラー詳細: {type(e).__name__}: {e}")
            print(f"     ❌ ダウンロードエラー。リトライしません")
            import traceback
            traceback.print_exc()
            return None
            
        except KeyboardInterrupt:
            print(f"\n     ⚠️ ユーザーによる中断検出")
            raise
            
        except Exception as e:
            print(f"\n     ❌ 予期しないエラー (試行 {attempt + 1}/{max_retries})")
            print(f"        エラータイプ: {type(e).__name__}")
            print(f"        エラー詳細: {e}")
            if attempt == max_retries - 1:
                print(f"     ❌ 最大リトライ回数に到達。ダウンロード失敗")
                import traceback
                traceback.print_exc()
                return None
    
    return None

# -------------------------
# 台本＋字幕つき動画生成
# -------------------------
def create_video_with_keywords(script_lines, keywords, api_key, voice_file, output_file="final_video.mp4"):
    print(f"\n🎬 動画生成開始: {output_file}")
    print(f"   台本行数: {len(script_lines)}")
    print(f"   キーワード数: {len(keywords)}")
    
    try:
        print(f"\n📊 ステップ1: 音声ファイル読み込み")
        narration = AudioFileClip(voice_file)
        total_duration = narration.duration
        dur_per_line = total_duration / len(script_lines)
        print(f"   音声長: {total_duration:.2f}秒")
        print(f"   1行あたり: {dur_per_line:.2f}秒")
        clips = []

        # 動画クリップを取得（新しいディレクトリに保存）
        print(f"\n📥 ステップ2: Pexels動画取得 ({len(keywords)}件)")
        video_files = []
        for i, kw in enumerate(keywords):
            print(f"\n[{i+1}/{len(keywords)}] キーワード: '{kw}'")
            urls = search_pexels_video(kw, api_key)
            clip_filename = ASSETS_VIDEO_DIR / f"clip_{i}_{os.getpid()}.mp4"
            vid_file = download_video(urls[0] if urls else "", str(clip_filename))
            video_files.append(vid_file)

    # 各台本行に動画を割り当て
        print(f"\n✂️ ステップ3: 動画クリップ作成 ({len(script_lines)}行)")
        for idx, line in enumerate(script_lines):
            print(f"  [{idx+1}/{len(script_lines)}] {line[:30]}...")
            vid_file = video_files[idx] if idx < len(video_files) else None
            if vid_file:
                try:
                    clip_raw = VideoFileClip(vid_file)
                    clip = clip_raw.subclipped(0, min(dur_per_line, clip_raw.duration))
                    bg = ColorClip((720,1280), (0,0,0), duration=clip.duration)
                    clip = CompositeVideoClip([bg, clip.resized(height=1280).with_position("center")])
                    print(f"     ✅ 動画クリップ作成完了")
                except Exception as e:
                    print(f"     ⚠️ 動画読み込みエラー: {e}、黒背景にフォールバック")
                    clip = ColorClip((720,1280), (0,0,0), duration=dur_per_line)
            else:
                # 足りない場合は黒背景
                print(f"     ⚠️ 動画なし、黒背景使用")
                clip = ColorClip((720,1280), (0,0,0), duration=dur_per_line)

            # 字幕
            img = create_subtitle_image(line)
            subtitle = ImageClip(img, transparent=True).with_duration(dur_per_line).with_position("center")
            clip = CompositeVideoClip([clip, subtitle])
            clips.append(clip)

        # ナレーションの長さに合わせて最後の動画を延長
        current_total = sum(c.duration for c in clips)
        print(f"\n⏱️ 時間調整: 現在{current_total:.2f}秒 / 必要{total_duration:.2f}秒")
        if current_total < total_duration:
            remain = total_duration - current_total
            print(f"   追加フィラー: {remain:.2f}秒")
            filler = ColorClip((720,1280), (0,0,0), duration=remain)
            last_img = create_subtitle_image(script_lines[-1])
            subtitle = ImageClip(last_img, transparent=True).with_duration(remain).with_position("center")
            clips.append(CompositeVideoClip([filler, subtitle]))

        print(f"\n🎞️ ステップ4: 動画結合＆音声合成")
        final = concatenate_videoclips(clips, method="compose").with_audio(narration)
        
        print(f"\n💾 ステップ5: ファイル書き込み中...")
        final.write_videofile(output_file, fps=24)
        
        file_size = os.path.getsize(output_file)
        print(f"\n✅ 動画生成完了: {output_file} ({file_size/1024/1024:.2f} MB)")
        
    except Exception as e:
        print(f"\n❌ 動画生成エラー: {e}")
        import traceback
        traceback.print_exc()
        raise

# -------------------------
# 実行例
# -------------------------
PEXELS_API_KEY = "QqcFiUzxOsDiOYP3sUQyty0hKhTGdzgBQdPQ8nymB7Y1KaXkYocVkctS"


# --- 各アカウント用台本・キーワード ---
accounts = [
    {
        "name": "心理テストラボ",
        "script": """あなたの本当の性格、当てられます\n1つだけ質問させてください\n朝起きて最初に見るものは何ですか？\n①スマホ ②時計 ③窓の外\n実は、これであなたの深層心理が丸わかり\n①を選んだあなた...まさか！\n人間関係で悩んでませんか？\n②の人は意外な才能の持ち主\n③を選んだ人、コメント欄集合！\nフォローで毎日診断配信中""",
        "keywords": ["psychology test", "personality", "morning routine", "smartphone", "window", "quiz", "human psychology", "relationship", "talent", "self discovery"],
        "output": "output/shinrigaku.mp4"
    },
    {
        "name": "闇夜の語り部",
        "script": """これは5年前、私が体験した話です\n深夜2時、帰宅途中の住宅街で\n向こうから歩いてくる女性がいた\nすれ違う瞬間、彼女が囁いた\n「後ろ...見ないで」\n振り返りそうになったその時\n背後から冷たい手が肩に...\n結局、私は振り返ってしまった\nそこにいたものは\nコメントで続き聞きたい人？""",
        "keywords": ["dark night", "horror story", "mysterious woman", "street", "whisper", "scary encounter", "urban legend", "supernatural", "suspense", "true horror"],
        "output": "output/kowaihanashi.mp4"
    },
    {
        "name": "映画紹介",
        "script": """この映画、ラスト5分で全てひっくり返る\n今話題の『時間泥棒』知ってる？\n主人公は記憶を失った探偵\n唯一の手がかりは謎のメモだけ\n事件を追うたび、時間が巻き戻る\n実は犯人、最初から画面に映ってた\n気づいた人いる？\n2回目観ると鳥肌止まらない\nネタバレ厳禁で拡散希望\nフォローで毎週新作紹介""",
        "keywords": ["mystery movie", "plot twist", "detective", "time", "memory loss", "thriller", "suspense film", "cinema", "movie review", "spoiler free"],
        "output": "output/movie.mp4"
    }
]


# 使い方：
# accounts = new_accounts  # 新しい収益化向け台本に差し替え

if __name__ == "__main__":
    # --- 生成したいアカウント名を指定 ---
    target_name = None  # 例: "映画紹介" など。Noneなら全て生成

    for acc in accounts:
        if target_name is not None and acc["name"] != target_name:
            continue
        print(f"\n=== {acc['name']} 動画生成 ===")
        script_lines = [line.strip() for line in acc["script"].split("\n") if line.strip()]
        # アカウントごとに話者・ピッチを設定
        if acc["name"] == "闇夜の語り部":
            speaker_index = 7
            pitch = -0.5
        else:
            speaker_index = 1
            pitch = 0
        # 音声ファイルはカレントディレクトリに出力
        voice_file_path = acc['output'].replace('output/', '').replace('.mp4', '.wav')
        voice_file = generate_voice(acc["script"], speaker_index=speaker_index, pitch=pitch, speed=1.0, filename=voice_file_path)
        # 動画ファイルのみoutputフォルダに出力
        create_video_with_keywords(script_lines, acc["keywords"], PEXELS_API_KEY, voice_file, output_file=acc["output"])
        print(f"✅ {acc['name']} 動画生成完了: {acc['output']}")

    print("✅ 動画生成完了")