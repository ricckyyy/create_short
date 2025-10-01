# --- 必要ライブラリ ---
# pip install moviepy pydub requests

import requests
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip, ColorClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

# VOICEVOX Engine API
VOICEVOX_API = "http://127.0.0.1:50021"

# -------------------------
# 字幕画像作成
# -------------------------
def create_subtitle_image(text, width=720, height=200, fontsize=30):
    font_path = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
    if os.name == "nt":
        font_path = "C:\\Windows\\Fonts\\msgothic.ttc"
    font = ImageFont.truetype(font_path, fontsize)
    img = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    lines = [text[i:i+20] for i in range(0, len(text), 20)]
    y = (height - len(lines)*(fontsize+10))//2
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font)
        w = bbox[2]-bbox[0]; x = (width-w)//2
        draw.text((x, y), line, font=font, fill="white")
        y += fontsize + 10
    return np.array(img)

def get_speakers():
    url = "http://localhost:50021/speakers"
    res = requests.get(url)
    if res.status_code != 200:
        raise Exception("VOICEVOX speakers API failed")
    return res.json()

# -------------------------
# VOICEVOX音声生成
# -------------------------
# VOICEVOX音声生成（ピッチや速度も調整可能）
# def generate_voice(text, speaker=1, pitch=0.0, speed=1.0, out_file="voice.wav"):
#     """
#     speaker: VOICEVOX話者ID
#     pitch: ピッチ補正（-1.0〜1.0, 0がデフォルト）
#     speed: 話速補正（0.5〜2.0くらい）
#     """
#     # audio_query
#     res = requests.post(f"{VOICEVOX_API}/audio_query", params={"text": text, "speaker": speaker})
#     if res.status_code != 200:
#         raise Exception("VOICEVOX audio_query failed")
#     data = res.json()

#     # ピッチ・速度を変更
#     data["speedScale"] = speed  # 話速
#     data["pitchScale"] = pitch  # ピッチ
#     # 必要に応じて他のパラメータも変更可能
#     # data["intonationScale"], data["volumeScale"], data["prePhonemeLength"], data["postPhonemeLength"]

#     # synthesis
#     res2 = requests.post(f"{VOICEVOX_API}/synthesis", json=data, params={"speaker": speaker})
#     with open(out_file, "wb") as f:
#         f.write(res2.content)
#     return out_file

def generate_voice(text, speaker_index=0, style_index=0, pitch=-0.5, speed=1.0, filename="voice.wav"):
    speakers = get_speakers()
    if speaker_index >= len(speakers):
        raise ValueError(f"speaker_index {speaker_index} は範囲外です")

    speaker = speakers[speaker_index]
    speaker_name = speaker["name"]
    
    if style_index >= len(speaker["styles"]):
        style_index = 0
    style_id = speaker["styles"][style_index]["id"]

    url_query = f"http://localhost:50021/audio_query"
    params = {"text": text, "speaker": style_id}
    res = requests.post(url_query, params=params)
    if res.status_code != 200:
        raise Exception("VOICEVOX audio_query failed")
    audio_query = res.json()

    audio_query["speedScale"] = speed
    audio_query["pitchScale"] = pitch

    url_speech = f"http://localhost:50021/synthesis?speaker={style_id}"
    res2 = requests.post(url_speech, json=audio_query)
    with open(filename, "wb") as f:
        f.write(res2.content)
    
    print(f"✅ 音声生成完了: {filename} （{speaker_name} / style={speaker['styles'][style_index]['name']})")
    return filename  # ターミナル用はファイルパスを返すだけ

# -------------------------
# Pexelsから動画URL取得
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
# 台本とキーワード対応版で動画作成
# -------------------------
def create_video_with_keywords(script_lines, keywords, api_key, voice_file, output_file="final_video.mp4"):
    narration = AudioFileClip(voice_file)
    dur_per_line = narration.duration / len(script_lines)
    clips = []

    for i, (line, kw) in enumerate(zip(script_lines, keywords)):
        # Pexels動画取得
        urls = search_pexels_video(kw, api_key)
        vid_file = download_video(urls[0] if urls else "", f"clip{i}.mp4")
        
        # 動画クリップを縦長にして黒背景に中央配置
        if vid_file:
            clip_raw = VideoFileClip(vid_file)
            clip_raw = clip_raw.subclipped(0, min(dur_per_line, clip_raw.duration))
            # 黒背景
            bg = ColorClip((720,1280), (0,0,0), duration=clip_raw.duration)
            clip = CompositeVideoClip([bg, clip_raw.resized(height=1280).with_position("center")])
        else:
            clip = ColorClip((720,1280), (0,0,0), duration=dur_per_line)

        # 字幕
        img = create_subtitle_image(line)
        subtitle = ImageClip(img, transparent=True).with_duration(dur_per_line).with_position("center")
        clip = CompositeVideoClip([clip, subtitle])
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose").with_audio(narration)
    final.write_videofile(output_file, fps=24)

# -------------------------
# 実行例
# -------------------------
PEXELS_API_KEY = "QqcFiUzxOsDiOYP3sUQyty0hKhTGdzgBQdPQ8nymB7Y1KaXkYocVkctS"
script = """
深夜、あなたは一人で部屋にいました。
スマホを見ていると、遠くから子守唄のような音が聞こえてきます。
耳を澄ますと、窓の外から囁く声が…
好奇心で窓の外を覗くと、誰もいません。
でも、背後で微かに「ねえ、遊ぼう…」と囁く声。
振り返ると、自分の影が勝手に動いていました。
あなたは恐怖で凍りつきます。
その瞬間、鏡に映る自分の姿が微笑みながら手を振っています。
"""
script_lines = script.strip().split("\n")

# 台本行ごとのキーワード
keywords = [
    "room alone night, creepy",
    "lullaby from distance, scary",
    "whisper outside window, mysterious",
    "looking outside, empty night, spooky",
    "whisper behind, eerie, ghost",
    "shadow moving alone, supernatural"
]

# 普通の声
# voice_file = generate_voice(script, speaker=1, pitch=0.0, speed=1.0, out_file="voice_normal.wav")

# 低めの声
voice_file = generate_voice(script, speaker_index=7, pitch=-0.5, speed=1)

# 高めの声
# voice_file = generate_voice(script, speaker=1, pitch=0.5, speed=1.1, out_file="voice_high.wav")

# voice_file = generate_voice(script, speaker=1, out_file="shikoku_metatan.wav")
create_video_with_keywords(script_lines, keywords, PEXELS_API_KEY, voice_file)
