"""
AI を使った台本自動生成スクリプト
OpenAI API / Anthropic Claude API / Ollama (ローカルLLM) を使用
過去の成功データから学習して最適化
"""

import os
import json
import random
from datetime import datetime
from pathlib import Path
from config import (
    ACCOUNTS,
    get_script_path,
    SCRIPTS_HISTORY_DIR,
    init_directories
)

# 学習モジュールをインポート
try:
    from learning_prompt import generate_learning_prompt, get_adaptive_instructions
    LEARNING_ENABLED = True
except ImportError:
    LEARNING_ENABLED = False
    print("⚠️ 学習機能が無効です（learning_prompt.pyが見つかりません）")

# ディレクトリ初期化
init_directories()

# 使用するAI API を選択（環境変数から取得）
# export USE_OLLAMA=true                   # Ollama (完全無料) - デフォルト有効
# export OPENAI_API_KEY="your-key"         # OpenAI
# export ANTHROPIC_API_KEY="your-key"      # Anthropic
USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() not in ("false", "0", "no")
USE_OPENAI = os.getenv("OPENAI_API_KEY") is not None
USE_ANTHROPIC = os.getenv("ANTHROPIC_API_KEY") is not None

if USE_OLLAMA:
    import requests
    OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
elif USE_OPENAI:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
elif USE_ANTHROPIC:
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 各アカウントのプロンプトテンプレート
ACCOUNT_PROMPTS = {
    "心理テストラボ": {
        "system": "あなたはTikTok/YouTube Shorts向けの心理テストコンテンツを作成するプロフェッショナルです。",
        "prompt": """
視聴維持率を最大化する心理テスト動画の台本を作成してください。

【要件】
- 10行（各行が1シーン）
- 冒頭2行で強烈なフックを作る
- 選択肢を提示（例: ①②③）
- 結果を小出しにして引き延ばす
- 最後にCTA（フォロー促進）
- エンゲージメント重視（コメント誘導）

【トーン】
- フレンドリー
- 共感を誘う
- サプライズ要素を入れる

【フォーマット】
各行を\\nで区切ったテキストのみを出力してください。説明は不要です。

例）
あなたの本当の性格、当てられます
1つだけ質問させてください
朝起きて最初に見るものは何ですか？
...（続く）

台本:
""",
        "keywords": ["psychology test", "personality", "quiz", "thinking", "brain", "mind", "decision making", "self discovery", "human nature", "character analysis"]
    },
    
    "闇夜の語り部": {
        "system": "あなたはTikTok/YouTube Shorts向けのホラーストーリーを作成するプロフェッショナルです。",
        "prompt": """
視聴維持率を最大化する怖い話動画の台本を作成してください。

【要件】
- 10行（各行が1シーン）
- 冒頭2行で不気味な雰囲気を作る
- 実体験風のリアリティ
- 徐々に恐怖を高めていく
- クリフハンガー（続きが気になる終わり方）
- 最後にエンゲージメント誘導

【トーン】
- シリアス
- 不穏な雰囲気
- リアリティのある描写

【フォーマット】
各行を\\nで区切ったテキストのみを出力してください。説明は不要です。

例）
これは5年前、私が体験した話です
深夜2時、帰宅途中の住宅街で
...（続く）

台本:
""",
        "keywords": ["dark night", "horror story", "mysterious", "scary", "urban legend", "supernatural", "suspense", "true horror", "nightmare", "paranormal"]
    },
    
    "映画紹介": {
        "system": "あなたはTikTok/YouTube Shorts向けの映画紹介コンテンツを作成するプロフェッショナルです。必ず実在する映画の正確な情報を使用してください。",
        "prompt": """
視聴維持率を最大化する映画紹介動画の台本を作成してください。

【絶対厳守事項】
- 必ず実在する有名映画を1作品選ぶこと（架空の映画は絶対NG）
- 映画の実際のあらすじや設定を正確に使うこと
- 知らない映画を創作してはいけない
- タイトルは『』で囲む
- 推奨作品: シックス・センス、君の名は。、インセプション、ショーシャンクの空に、タイタニック、千と千尋の神隠し、インターステラー、ダークナイト、天気の子、すずめの戸締まり

【内容の正確性】
- 映画の実際のストーリー要素のみ使用
- 主要キャラクターや設定は事実に基づく
- 有名なシーンや評価ポイントを正確に紹介
- 憶測や創作は一切禁止

【要件】
- 10行（各行が1シーン）
- 冒頭で映画タイトルと魅力を提示
- ネタバレ厳禁のティーザー風
- 実際の見どころを紹介
- 最後にフォロー促進

【トーン】
- 情熱的で正確
- 興味を引くがネタバレしない
- 実際の映画体験に忠実

【フォーマット】
各行を\\nで区切ったテキストのみ。説明不要。

例）
この映画、ラスト5分で全てひっくり返る
『シックス・センス』観た人いる？
主人公は死者が見える少年
心理学者が唯一の理解者
でも最後に明かされる真実
実は彼も...
全てのシーンが伏線だった
2回観て初めて気づく仕掛け
映画史に残る名作
フォローで毎週名作紹介

台本:
""",
        "keywords": ["mystery movie", "plot twist", "cinema", "thriller", "suspense film", "movie review", "spoiler free", "must watch", "hidden gem", "masterpiece"]
    }
}


def generate_script_with_ollama(account_name):
    """Ollama (ローカルLLM) で台本生成 - 学習機能付き"""
    config = ACCOUNT_PROMPTS[account_name]
    
    # 学習プロンプトを生成（データがあれば）
    base_prompt = f"{config['system']}\n\n{config['prompt']}"
    
    if LEARNING_ENABLED:
        try:
            # 過去の成功パターンを組み込む
            enhanced_prompt = generate_learning_prompt(account_name, base_prompt)
            print(f"🎓 学習データを活用してプロンプト生成")
        except Exception as e:
            print(f"⚠️ 学習プロンプト生成失敗、ベースプロンプトを使用: {e}")
            enhanced_prompt = base_prompt
    else:
        enhanced_prompt = base_prompt
    
    # 明確な例を含めて品質向上
    example = """例:
この心理テスト、当たりすぎてヤバい
1つだけ質問させてください
今すぐ食べたいものは？
①甘いもの ②辛いもの ③しょっぱいもの
これであなたの性格が丸わかり
①を選んだあなた...実は寂しがり屋
②は情熱的で行動派のタイプ
③を選んだ人、コメントで教えて
フォローで毎日診断配信中"""
    
    prompt = f"""{enhanced_prompt}

{example if account_name == "心理テストラボ" else ""}

上記のルールを守ってください:
1. 10行ちょうどで書く
2. 各行は短く、テンポよく
3. 冒頭で引き込む
4. 最後はフォロー促進
5. 「台本:」などの余計な文字は書かない
6. 例や説明は一切不要

それでは、{account_name}向けの台本を10行で書いてください:"""
    
    max_retries = 3
    import time
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait_time = 2 ** attempt
                print(f"   ⏳ リトライ {attempt + 1}/{max_retries} - {wait_time}秒待機...")
                time.sleep(wait_time)
            
            print(f"   📡 Ollama API接続中... (試行 {attempt + 1}/{max_retries})")
            response = requests.post(
                OLLAMA_API_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 400,
                        "top_p": 0.9,
                        "repeat_penalty": 1.1
                    }
                },
                timeout=90
            )
            response.raise_for_status()
            result = response.json()
            script = result.get("response", "").strip()
            
            if not script:
                raise ValueError("Ollama returned empty response")
            
            print(f"   ✅ Ollama応答受信 ({len(script)}文字)")
            
            # クリーニング
            lines = []
            for line in script.split('\n'):
                line = line.strip()
                # 番号付きリストや不要な接頭辞を削除
                if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                    line = line.split('.', 1)[1].strip()
                if line and not line.startswith(('台本', '以下', '例:', '---')):
                    lines.append(line)
            
            print(f"   📊 クリーニング後: {len(lines)}行")
            
            # 行数調整
            if len(lines) > 10:
                lines = lines[:10]
                print(f"   ✂️ 10行にトリミング")
            elif len(lines) < 5:  # 5行未満は品質が悪すぎるのでリトライ
                if attempt < max_retries - 1:
                    print(f"   ⚠️ {len(lines)}行しか生成されませんでした。リトライします...")
                    raise ValueError(f"Generated only {len(lines)} valid lines (minimum 5)")
                else:
                    # 最終試行では補完して続行
                    print(f"   ⚠️ {len(lines)}行のみ。不足分を補完します...")
                    while len(lines) < 5:
                        lines.append("フォローで毎日更新中")
            # 5～10行はそのまま使用（補完しない）
            
            print(f"   ✅ 最終: {len(lines)}行")
            return '\n'.join(lines)
            
        except requests.exceptions.Timeout as e:
            print(f"   ⏱️ タイムアウト発生 (試行 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                print(f"   ❌ 最大リトライ回数に到達。Ollama接続失敗")
                raise
                
        except requests.exceptions.ConnectionError as e:
            print(f"   🔌 接続エラー発生 (試行 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                print(f"   ❌ 最大リトライ回数に到達。接続失敗")
                raise
                
        except KeyboardInterrupt:
            print(f"\n   ⚠️ ユーザーによる中断検出")
            raise
            
        except Exception as e:
            print(f"   ❌ エラー (試行 {attempt + 1}/{max_retries}): {type(e).__name__}: {e}")
            if attempt == max_retries - 1:
                raise
    
    # ここには到達しないはずだが、念のため
    raise Exception("Ollama API呼び出しに失敗しました")


def generate_script_with_openai(account_name):
    """OpenAI API で台本生成"""
    config = ACCOUNT_PROMPTS[account_name]
    
    response = openai.ChatCompletion.create(
        model="gpt-4",  # または "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": config["system"]},
            {"role": "user", "content": config["prompt"]}
        ],
        temperature=0.9,  # 創造性を高める
        max_tokens=500
    )
    
    script = response.choices[0].message.content.strip()
    return script


def generate_script_with_anthropic(account_name):
    """Anthropic Claude API で台本生成"""
    config = ACCOUNT_PROMPTS[account_name]
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # または他のモデル
        max_tokens=1024,
        messages=[
            {"role": "user", "content": config["system"] + "\n\n" + config["prompt"]}
        ],
        temperature=0.9
    )
    
    script = message.content[0].text.strip()
    return script


def generate_script_fallback(account_name):
    """API が使えない場合のフォールバック（ランダムテンプレート）"""
    templates = {
        "心理テストラボ": [
            """あなたの隠れた才能、見抜きます\n簡単な質問に答えてください\n好きな季節は何ですか?\n①春 ②夏 ③秋 ④冬\nこれであなたの本質が分かります\n①を選んだ人、実は...\n周りを明るくする力を持ってる\n②の人は情熱的な性格\n③④の人、コメントで教えて\nフォローで明日も診断配信""",
            """直感で選んでください\n今すぐ行きたい場所は?\n①海 ②山 ③街 ④家\nこれで性格が丸わかり\n①海を選んだあなた\n実は自由を求めてますね?\n②山の人は冒険家タイプ\n③④を選んだ人は?\nコメント欄で語り合おう\n毎日更新中、フォロー必須"""
        ],
        "闇夜の語り部": [
            """昨夜、変な夢を見ました\n暗い廊下を歩いていると\n奥から女性の声が聞こえる\n「こっち...来ないで」\nでも足が勝手に進んでしまう\nドアを開けた瞬間\n鏡に映る自分が笑ってた\nそして今朝、鏡に手形が\nまだそこにあります\nこれ、夢だったのかな?""",
            """3日前から部屋で足音がする\n夜中の3時、必ず同じ時間\n誰もいないのに廊下を歩く音\n昨日、勇気を出して確認した\n何もいない...はずだった\nでも床に濡れた足跡\nしかもだんだん近づいてくる\n今夜も3時が来る\n助けて\nこれ、どうしたらいい?"""
        ],
        "映画紹介": [
            """このラスト、鳥肌止まらない\n『シックス・センス』観た人いる?\n主人公は死者が見える少年\n誰にも信じてもらえない苦しみ\nでも心理学者だけが寄り添う\nそして衝撃のラスト5分\n全てがひっくり返る瞬間\n2回観ないと気づかない伏線\n映画史に残る名作\nフォローで毎週おすすめ紹介""",
            """予告編だけで泣いた\n『君の名は。』が超話題\n入れ替わる二人の運命\n会いたいのに会えない理由\nタイムリミットは隕石落下\n真実を知った時、あなたは?\n最後の「好きだ」で涙腺崩壊\nこの映画、人生変わる\nまだ観てない人は今すぐ\n新作情報はフォローから""",
            """この映画、全てひっくり返る\n『インセプション』知ってる?\n夢の中に侵入する泥棒\n現実と夢の境界が曖昧に\nラストシーンのコマは?\n今も議論が絶えない結末\n3回観ても新発見がある\n映画ファン必見の傑作\nディカプリオ最高傑作\nフォローで名作を紹介中"""
        ]
    }
    
    return random.choice(templates.get(account_name, [templates["心理テストラボ"][0]]))


def generate_script(account_name):
    """台本を生成（利用可能なAPIを自動選択）"""
    try:
        if USE_OLLAMA:
            print(f"🦙 Ollama ({OLLAMA_MODEL}) で {account_name} の台本を生成中...")
            return generate_script_with_ollama(account_name)
        elif USE_OPENAI:
            print(f"🤖 OpenAI GPT-4 で {account_name} の台本を生成中...")
            return generate_script_with_openai(account_name)
        elif USE_ANTHROPIC:
            print(f"🤖 Claude で {account_name} の台本を生成中...")
            return generate_script_with_anthropic(account_name)
        else:
            print(f"⚠️ AI未設定。テンプレートから {account_name} の台本を選択...")
            return generate_script_fallback(account_name)
    except Exception as e:
        print(f"❌ エラー: {e}")
        print(f"⚠️ フォールバックテンプレートを使用...")
        return generate_script_fallback(account_name)


def save_script_history(account_name, script):
    """台本履歴を保存"""
    date_str = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%H%M%S")
    
    script_path = get_script_path(account_name, date_str, timestamp)
    
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)
    
    print(f"📝 台本を保存: {script_path}")


def generate_all_scripts():
    """全アカウントの台本を生成"""
    accounts_data = []
    date_str = datetime.now().strftime("%Y%m%d")
    
    for account_name in ACCOUNTS.keys():
        print(f"\n{'='*50}")
        print(f"🎬 {account_name}")
        print('='*50)
        
        script = generate_script(account_name)
        keywords = ACCOUNT_PROMPTS[account_name]["keywords"]
        
        # キーワードをランダムにシャッフル（バリエーション追加）
        random.shuffle(keywords)
        
        account_config = ACCOUNTS[account_name]
        
        account_data = {
            "name": account_name,
            "script": script,
            "keywords": keywords,
            "slug": account_config["slug"]
        }
        
        accounts_data.append(account_data)
        
        # 履歴保存
        save_script_history(account_name, script)
        
        print(f"\n📄 生成された台本:")
        print("-" * 50)
        print(script)
        print("-" * 50)
    
    # JSON形式で保存（スクリプト履歴ディレクトリに）
    output_file = SCRIPTS_HISTORY_DIR / f"scripts_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(accounts_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 全台本を生成完了: {output_file}")
    return accounts_data


if __name__ == "__main__":
    print("🚀 AI 台本生成スタート")
    print(f"📅 日付: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    
    if USE_OPENAI:
        print("🔑 使用API: OpenAI GPT-4")
    elif USE_ANTHROPIC:
        print("🔑 使用API: Anthropic Claude")
    else:
        print("⚠️ APIキー未設定 - テンプレートモードで動作")
    
    accounts = generate_all_scripts()
    
    print("\n" + "="*50)
    print("✅ 完了！")
    print("="*50)
