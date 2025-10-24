# --- 必要ライブラリ ---
# pip install moviepy pydub requests

import os
os.makedirs("output", exist_ok=True)

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

    # 動画クリップを取得
    video_files = []
    for i, kw in enumerate(keywords):
        urls = search_pexels_video(kw, api_key)
        vid_file = download_video(urls[0] if urls else "", f"clip{i}.mp4")
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
        "script": """
【驚愕】1分で分かるあなたの恋愛観診断！\nあなたは今、恋愛で悩んでいませんか？\n3つの質問であなたの運命がわかります！\n1つ目：好きな人からLINEが来たら...\n①すぐ返信 ②じっくり考える ③気分で対応\nえっ！まさかあなた...！？\nそして2問目の質問で運命が変わる...\n実は2番を選んだ人には、意外な結果が！\nフォロー＆いいねで次回の質問へ\n結果を知りたい人は@shinri_labo まで！\n""",
        "keywords": ["love", "psychology", "test", "personality", "diagnosis", "relationship", "fortune", "line", "romance", "future"],
        "output": "output/shinrigaku.mp4"
    },
    {
        "name": "闇夜の語り部",
        "script": """
⚠️この動画は深夜の視聴を推奨します\n都内某所で起きた本当の怖い話...\nコンビニの夜勤中、不思議な出来事が\n誰もいない店内なのに、レジの呼び出し音が\nカメラを確認すると、レジ前に見知らぬ女性が\nでも、店内には誰もいないはず...\n監視カメラに映っていたものは？\n続きが気になる人はフォロー必須！\n毎週火曜の深夜に投稿中\nもっと怖い話は@yami_kataribe で！\n""",
        "keywords": ["horror", "ghost", "convenience store", "night", "mystery", "scary", "urban legend", "security camera", "supernatural", "true story"],
        "output": "output/kowaihanashi.mp4"
    },
    {
        "name": "映画紹介",
        "script": """
全世界で話題沸騰！涙腺崩壊の傑作が解禁\nNetflix新作『あの日の約束』\n幼なじみの親友を事故で亡くした主人公\nある日、10年前からの手紙が届く...\nこの映画、最後の5分で人生観が変わります\n世界中で"心が浄化された"と話題に\nここからが本当の見どころ...\n予想を超える結末の考察を待ってます！\nフォローで次回作もお見逃しなく\nレビューは@movie_review で配信中！\n""",
        "keywords": ["movie", "netflix", "drama", "friendship", "letter", "emotion", "review", "recommendation", "twist", "masterpiece"],
        "output": "output/movie.mp4"
    }
]


# 使い方：
# accounts = new_accounts  # 新しい収益化向け台本に差し替え

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