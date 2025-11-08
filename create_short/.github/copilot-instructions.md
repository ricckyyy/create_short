# AI Coding Agent Instructions

## Project Overview
This is a **TikTok/YouTube Shorts video automation pipeline** that generates short-form vertical videos (720x1280) with narration, subtitles, and stock footage for three content accounts:
1. **心理テストラボ** (Psychology Tests) - personality/psychology quizzes
2. **闇夜の語り部** (Dark Storyteller) - horror stories/urban legends  
3. **映画紹介** (Movie Reviews) - film recommendations

## Core Architecture
**Single-file pipeline** (`create_movie.py`) orchestrates:
1. **Script → Voice** (VOICEVOX TTS API)
2. **Keywords → Videos** (Pexels API)
3. **Assembly** (MoviePy) - concatenate clips, overlay subtitles, sync audio

### Key Data Flow
```
accounts[] dict → generate_voice() → create_video_with_keywords() → output/*.mp4
                     ↓                    ↓
                  voice.wav          Pexels search + download
```

## Critical Dependencies
- **VOICEVOX Engine**: Local TTS server at `http://127.0.0.1:50021` (must be running)
- **Pexels API**: Stock video source (`PEXELS_API_KEY` hardcoded in script)
- **MoviePy + PIL**: Video composition and subtitle rendering

## Account-Specific Patterns
Each account in `accounts[]` follows this structure:
```python
{
    "name": str,           # Account identifier
    "script": str,         # Narration text (newline-separated)
    "keywords": [str],     # Pexels search terms (1 per script line ideally)
    "output": str          # output/*.mp4 path
}
```

**Voice customization** (see bottom of `create_movie.py`):
- 闇夜の語り部: `speaker_index=7, pitch=-0.5` (deeper voice for horror)
- Others: `speaker_index=1, pitch=0` (default)

## Subtitle System
- **Rendering**: `create_subtitle_image()` generates RGBA PIL images with white text + black outline
- **Layout**: Auto-wraps at 20 characters/line, vertically centered
- **Font paths**: 
  - Linux: `/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc`
  - Windows: `C:\Windows\Fonts\msgothic.ttc`

## Script Content Guidelines (`daihon.md`)
Scripts must optimize for **watch time & engagement**:
- Hook in first 2 seconds
- ~10 lines per script (avoid overly long narration)
- End with CTA (follow/comment prompt)
- Tone varies by account (quiz-style vs. spooky vs. informative)

## Common Workflows

### Generate Video for One Account
```python
target_name = "映画紹介"  # Set specific account name
# Script auto-skips others in loop
```

### Add New Account
1. Add entry to `accounts[]` list
2. Define `keywords[]` matching script line count
3. Optionally customize voice in generation loop

### Debug Video Issues
- Check VOICEVOX is running: `curl http://127.0.0.1:50021/speakers`
- Verify Pexels API key validity
- Ensure `output/` directory exists (auto-created by script)

## File Outputs
- **Audio**: `{account_name}.wav` in current directory
- **Video**: `output/{account_name}.mp4` 
- **Temp clips**: `clip{i}.mp4` (downloaded Pexels videos, not cleaned up)

## Critical Constraints
1. **Duration sync**: `create_video_with_keywords()` divides narration duration equally across script lines
2. **Vertical format**: Hardcoded 720x1280 (TikTok/Shorts standard)
3. **No error recovery**: Script assumes APIs succeed (add try/except for production)
4. **Temp file management**: Downloaded clips aren't deleted after use

## When Modifying Scripts
- Keep keyword count ≥ script line count (avoid black filler clips)
- Test voice generation separately before full video render
- Verify font paths exist on target OS
- Consider narration duration when adding lines (impacts pacing)
