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
    font_path = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
    if os.name == "nt":
        font_path = "C:\\Windows\\Fonts\\msgothic.ttc"
    font = ImageFont.truetype(font_path, fontsize)
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
    speakers = get_speakers()
    if speaker_index >= len(speakers):
        raise ValueError(f"speaker_index {speaker_index} は範囲外です")

    speaker = speakers[speaker_index]
    speaker_name = speaker["name"]
    
    if style_index >= len(speaker["styles"]):
        style_index = 0
    style_id = speaker["styles"][style_index]["id"]

    # audio_query
    url_query = f"{VOICEVOX_API}/audio_query"
    res = requests.post(url_query, params={"text": text, "speaker": style_id})
    res.raise_for_status()
    audio_query = res.json()

    # ピッチ・速度調整
    audio_query["speedScale"] = speed
    audio_query["pitchScale"] = pitch

    # synthesis
    url_speech = f"{VOICEVOX_API}/synthesis?speaker={style_id}"
    res2 = requests.post(url_speech, json=audio_query)
    with open(filename, "wb") as f:
        f.write(res2.content)

    print(f"✅ 音声生成完了: {filename} （{speaker_name} / style={speaker['styles'][style_index]['name']})")
    return filename

# -------------------------
# Pexels: 動画検索
# -------------------------
def search_pexels_video(query, api_key, max_results=1):
    headers = {"Authorization": api_key}
    r = requests.get("https://api.pexels.com/videos/search", headers=headers, params={"query": query, "per_page": max_results})
    vs = r.json().get("videos", [])
    urls = [v["video_files"][0]["link"] for v in vs if v.get("video_files")]
    return urls

# -------------------------
# 動画ダウンロード
# -------------------------
def download_video(url, filename):
    if not url:
        return None
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(1024):
            if chunk:
                f.write(chunk)
    return filename

# -------------------------
# 台本＋字幕つき動画生成
# -------------------------
def create_video_with_keywords(script_lines, keywords, api_key, voice_file, output_file="final_video.mp4"):
    narration = AudioFileClip(voice_file)
    total_duration = narration.duration
    dur_per_line = total_duration / len(script_lines)
    clips = []

    # 動画クリップを取得（新しいディレクトリに保存）
    video_files = []
    for i, kw in enumerate(keywords):
        urls = search_pexels_video(kw, api_key)
        clip_filename = ASSETS_VIDEO_DIR / f"clip_{i}_{os.getpid()}.mp4"
        vid_file = download_video(urls[0] if urls else "", str(clip_filename))
        video_files.append(vid_file)

    # 各台本行に動画を割り当て
    for idx, line in enumerate(script_lines):
        vid_file = video_files[idx] if idx < len(video_files) else None
        if vid_file:
            clip_raw = VideoFileClip(vid_file)
            clip = clip_raw.subclipped(0, min(dur_per_line, clip_raw.duration))
            bg = ColorClip((720,1280), (0,0,0), duration=clip.duration)
            clip = CompositeVideoClip([bg, clip.resized(height=1280).with_position("center")])
        else:
            # 足りない場合は黒背景
            clip = ColorClip((720,1280), (0,0,0), duration=dur_per_line)

        # 字幕
        img = create_subtitle_image(line)
        subtitle = ImageClip(img, transparent=True).with_duration(dur_per_line).with_position("center")
        clip = CompositeVideoClip([clip, subtitle])
        clips.append(clip)

    # ナレーションの長さに合わせて最後の動画を延長
    current_total = sum(c.duration for c in clips)
    if current_total < total_duration:
        remain = total_duration - current_total
        filler = ColorClip((720,1280), (0,0,0), duration=remain)
        last_img = create_subtitle_image(script_lines[-1])
        subtitle = ImageClip(last_img, transparent=True).with_duration(remain).with_position("center")
        clips.append(CompositeVideoClip([filler, subtitle]))

    final = concatenate_videoclips(clips, method="compose").with_audio(narration)
    final.write_videofile(output_file, fps=24)

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