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

        # 黒い縁取りを描画（上下左右＋斜め）
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    draw.text((x+dx, y+dy), line, font=font, fill="black")

        # 白文字を上に描画
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

        # 動画クリップ準備
        if vid_file:
            clip_raw = VideoFileClip(vid_file)
            clip_raw = clip_raw.subclipped(0, min(dur_per_line, clip_raw.duration))
            bg = ColorClip((720,1280), (0,0,0), duration=clip_raw.duration)
            clip = CompositeVideoClip([bg, clip_raw.resized(height=1280).with_position("center")])
        else:
            clip = ColorClip((720,1280), (0,0,0), duration=dur_per_line)

        # 字幕（縁付き）
        img = create_subtitle_image(line)
        subtitle = ImageClip(img, transparent=True).with_duration(dur_per_line).with_position(("center","bottom"))
        clip = CompositeVideoClip([clip, subtitle])
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose").with_audio(narration)
    final.write_videofile(output_file, fps=24)

# -------------------------
# 実行例
# -------------------------
PEXELS_API_KEY = "QqcFiUzxOsDiOYP3sUQyty0hKhTGdzgBQdPQ8nymB7Y1KaXkYocVkctS"

script = """
【映画紹介：ショーシャンクの空に】
無実の罪で投獄された銀行員アンディ。
絶望的な環境の中でも希望を失わず、
仲間と友情を築きながら自由を求め続けます。

この映画は「希望を持つことの強さ」を描いた名作。
公開当初はヒットしませんでしたが、
口コミやランキングで評価が高まり、
今では不朽の名作と呼ばれています。

観終わった後に必ず勇気をもらえる、
映画ファン必見の作品です。
"""

# 素材収集用英語キーワード（Pexels向け）
keywords = ["prison", "friendship", "hope", "cinematic", "freedom"]

# ハッシュタグ（コピペ用）
#映画紹介 #名作映画 #ショーシャンクの空に #おすすめ映画 #映画好き


script_lines = [line.strip() for line in script.split("\n") if line.strip()]

# 低めの声
# voice_file = generate_voice(script, speaker_index=7, pitch=-0.5, speed=1)
voice_file = generate_voice(script, speaker_index=1, pitch=0.0, speed=1)

# voice_file = generate_voice(script, speaker=1, out_file="shikoku_metatan.wav")
create_video_with_keywords(script_lines, keywords, PEXELS_API_KEY, voice_file)
