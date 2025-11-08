"""
AI を使った台本自動生成スクリプト
OpenAI API または Anthropic Claude API を使用
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

# ディレクトリ初期化
init_directories()

# 使用するAI API を選択（環境変数から取得）
# export OPENAI_API_KEY="your-key" または export ANTHROPIC_API_KEY="your-key"
USE_OPENAI = os.getenv("OPENAI_API_KEY") is not None
USE_ANTHROPIC = os.getenv("ANTHROPIC_API_KEY") is not None

if USE_OPENAI:
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
        "system": "あなたはTikTok/YouTube Shorts向けの映画紹介コンテンツを作成するプロフェッショナルです。",
        "prompt": """
視聴維持率を最大化する映画紹介動画の台本を作成してください。

【要件】
- 10行（各行が1シーン）
- 冒頭2行で映画の魅力を提示
- 架空の映画でも実在の映画でもOK
- ネタバレ厳禁のティーザー風
- どんでん返しや意外な要素を匂わす
- 最後にフォロー促進

【トーン】
- 情熱的
- 興味を引く
- ネタバレしない配慮

【フォーマット】
各行を\\nで区切ったテキストのみを出力してください。説明は不要です。

例）
この映画、ラスト5分で全てひっくり返る
今話題の『時間泥棒』知ってる？
...（続く）

台本:
""",
        "keywords": ["mystery movie", "plot twist", "cinema", "thriller", "suspense film", "movie review", "spoiler free", "must watch", "hidden gem", "masterpiece"]
    }
}


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
            """このラスト、鳥肌止まらない\n『記憶の檻』観た人いる?\n主人公は目覚めると記憶喪失\n毎日メモだけが唯一の手がかり\nでも誰かがメモを書き換えてる\n信じられるのは自分だけ\nそして衝撃のラスト15秒\n全員が涙した名シーン\n映画館で観て欲しい\nフォローで毎週おすすめ紹介""",
            """予告編だけで泣いた\n『最後の約束』が超話題\n余命宣告された主人公が\n大切な人に嘘をつく理由\nタイムリミットは30日\n真実を知った時、あなたは?\n2回観ないと気づかない伏線\nこの映画、人生変わる\nネタバレ厳禁で広めて\n新作情報はフォローから"""
        ]
    }
    
    return random.choice(templates.get(account_name, [templates["心理テストラボ"][0]]))


def generate_script(account_name):
    """台本を生成（利用可能なAPIを自動選択）"""
    try:
        if USE_OPENAI:
            print(f"🤖 OpenAI GPT-4 で {account_name} の台本を生成中...")
            return generate_script_with_openai(account_name)
        elif USE_ANTHROPIC:
            print(f"🤖 Claude で {account_name} の台本を生成中...")
            return generate_script_with_anthropic(account_name)
        else:
            print(f"⚠️ API未設定。テンプレートから {account_name} の台本を選択...")
            return generate_script_fallback(account_name)
    except Exception as e:
        print(f"❌ API エラー: {e}")
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
