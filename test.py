import requests

# -----------------------------
# VOICEVOXで全キャラクター取得
# -----------------------------
def get_speakers():
    url = "http://localhost:50021/speakers"
    res = requests.get(url)
    if res.status_code != 200:
        raise Exception("VOICEVOX speakers API failed")
    return res.json()

# -----------------------------
# 音声生成関数（speaker_index対応）
# -----------------------------
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

# -----------------------------
# サンプル実行
# -----------------------------
script = "これはテストです。声を切り替えて読みます。"
generate_voice(script, speaker_index=0, style_index=0, pitch=-0.5, speed=1, filename="music/shikoku.wav")
# generate_voice(script, speaker_index=1, style_index=0, pitch=-0.5, speed=1.0, filename="music/zunda.wav")
# generate_voice(script, speaker_index=3, style_index=0, pitch=-0.5, speed=1.0, filename="music/natsuki.wav")
# generate_voice(script, speaker_index=4, style_index=0, pitch=-0.5, speed=1.0, filename="music/haruka.wav")
# generate_voice(script, speaker_index=5, style_index=0, pitch=-0.5, speed=1.0, filename="music/hikari.wav")
# generate_voice(script, speaker_index=6, style_index=0, pitch=-0.5, speed=1.0, filename="music/takeru.wav")
# generate_voice  (script, speaker_index=7, style_index=0, pitch=-0.5, speed=1.0, filename="music/santa.wav")
# generate_voice(script, speaker_index=8, style_index=0, pitch=-0.5, speed=1.0, filename="music/goemon.wav")
# generate_voice(script, speaker_index=9, style_index=0, pitch=-0.5, speed=1.0, filename="music/kiritan.wav")
# generate_voice(script, speaker_index=10, style_index=0, pitch=-0.5, speed=1.0, filename="music/akane.wav")
# generate_voice(script, speaker_index=11, style_index=0, pitch=-0.5, speed=1.0, filename="music/ayumu.wav")
# generate_voice(script, speaker_index=12, style_index=0, pitch=-0.5, speed=1.0, filename="music/fuka.wav")
# generate_voice(script, speaker_index=13, style_index=0, pitch=-0.5, speed=1.0, filename="music/mizuki.wav")
# generate_voice(script, speaker_index=14, style_index=0, pitch=-0.5, speed=1.0, filename="music/shouta.wav")
# generate_voice(script, speaker_index=15, style_index=0, pitch=-0.5, speed=1.0, filename="music/sora.wav")
# generate_voice(script, speaker_index=16, style_index=0, pitch=-0.5, speed=1.0, filename="music/yuzuki.wav")
# generate_voice(script, speaker_index=17, style_index=0, pitch=-0.5, speed=1.0, filename="music/tenshi.wav")
# generate_voice(script, speaker_index=18, style_index=0, pitch=-0.5, speed=1.0, filename="music/miku.wav")
# generate_voice(script, speaker_index=19, style_index=0, pitch=-0.5, speed=1.0, filename="music/luka.wav")
# generate_voice(script, speaker_index=20, style_index=0, pitch=-0.5, speed=1.0, filename="music/meiko.wav") 
