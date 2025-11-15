#!/usr/bin/env python3
"""
AI学習プロンプト生成モジュール
過去の成功データから学習してプロンプトを最適化
"""

import json
from analytics import analyze_successful_scripts, generate_insights
from db_manager import get_top_videos


def generate_learning_prompt(account_name, base_prompt=""):
    """
    過去の成功事例から学習してプロンプトを生成
    
    Args:
        account_name: アカウント名
        base_prompt: ベースとなるプロンプト
    
    Returns:
        str: 学習要素を組み込んだプロンプト
    """
    # 成功事例を分析
    analysis = analyze_successful_scripts(account_name, top_n=5)
    
    if analysis.get("status") == "no_data":
        # データがない場合はベースプロンプトのみ
        return base_prompt
    
    # 成功パターンを抽出
    top_videos = get_top_videos(account_name, limit=3)
    successful_examples = []
    
    for video in top_videos:
        successful_examples.append({
            "title": video["title"],
            "script": video["script_content"],
            "views": video["views"]
        })
    
    # プロンプトに組み込む学習要素
    learning_elements = []
    
    # 1. 成功した冒頭パターン
    opening_data = analysis.get("opening_patterns", {})
    if opening_data.get("question_rate", 0) > 0.5:
        learning_elements.append("- 冒頭は疑問形で始めると効果的")
    
    if opening_data.get("top_openings"):
        top_opening = opening_data["top_openings"][0]
        learning_elements.append(f"- 成功例の冒頭: 「{top_opening['text']}」")
    
    # 2. 最適な長さ
    content_length = analysis.get("content_length", {})
    if content_length.get("best_performing"):
        best = content_length["best_performing"]
        learning_elements.append(f"- 最適な行数: {best['line_count']}行程度")
    
    # 3. 効果的なキーワード
    keywords = analysis.get("keyword_frequency", {}).get("top_keywords", [])
    if keywords:
        top_kw = [k["keyword"] for k in keywords[:3]]
        learning_elements.append(f"- 効果的なキーワード: {', '.join(top_kw)}")
    
    # 4. 効果的なCTA
    cta_data = analysis.get("cta_patterns", {})
    if cta_data.get("avg_follow_views", 0) > analysis.get("avg_views", 0):
        learning_elements.append("- CTAは「フォロー」促進が効果的")
    elif cta_data.get("avg_comment_views", 0) > analysis.get("avg_views", 0):
        learning_elements.append("- CTAは「コメント」促進が効果的")
    
    # 5. 成功事例
    if successful_examples:
        best_example = successful_examples[0]
        learning_elements.append(f"- 最高再生数({best_example['views']}回)の台本構成を参考に")
    
    # プロンプト生成
    enhanced_prompt = f"""{base_prompt}

【過去の成功パターンを活用】
{chr(10).join(learning_elements)}

【成功事例（再生数トップ）】
タイトル: {successful_examples[0]['title']}
台本:
{successful_examples[0]['script']}

上記の成功パターンを活かしながら、新しい切り口で台本を作成してください。
"""
    
    return enhanced_prompt


def get_adaptive_instructions(account_name):
    """
    アカウント別の適応的な指示を生成
    
    Returns:
        dict: 指示内容
    """
    analysis = analyze_successful_scripts(account_name, top_n=10)
    insights = generate_insights(account_name)
    
    if analysis.get("status") == "no_data":
        return {
            "status": "no_learning",
            "message": "学習データ不足。デフォルト設定を使用します。"
        }
    
    # データ駆動型の指示
    instructions = {
        "status": "learning_active",
        "opening_style": "",
        "target_length": 0,
        "cta_recommendation": "",
        "keywords_to_use": []
    }
    
    # 冒頭スタイル
    opening_data = analysis.get("opening_patterns", {})
    if opening_data.get("question_rate", 0) > 0.5:
        instructions["opening_style"] = "疑問形で始める"
    elif opening_data.get("exclamation_rate", 0) > 0.5:
        instructions["opening_style"] = "感嘆形で始める"
    else:
        instructions["opening_style"] = "宣言形で始める"
    
    # 目標行数
    content_length = analysis.get("content_length", {})
    if content_length.get("best_performing"):
        instructions["target_length"] = content_length["best_performing"]["line_count"]
    
    # CTAレコメンデーション
    cta_data = analysis.get("cta_patterns", {})
    if cta_data.get("avg_follow_views", 0) > analysis.get("avg_views", 0):
        instructions["cta_recommendation"] = "フォロー促進"
    else:
        instructions["cta_recommendation"] = "コメント促進"
    
    # 推奨キーワード
    keywords = analysis.get("keyword_frequency", {}).get("top_keywords", [])
    instructions["keywords_to_use"] = [k["keyword"] for k in keywords[:5]]
    
    return instructions


if __name__ == "__main__":
    # テスト
    print("🤖 AI学習プロンプト生成テスト\n")
    
    account_name = "心理テストラボ"
    base_prompt = f"{account_name}向けの魅力的な台本を10行で作成してください。"
    
    print(f"📝 ベースプロンプト:\n{base_prompt}\n")
    print("="*60)
    print()
    
    # 学習プロンプト生成
    enhanced = generate_learning_prompt(account_name, base_prompt)
    print(f"🎯 学習強化プロンプト:\n{enhanced}\n")
    print("="*60)
    print()
    
    # 適応的指示取得
    instructions = get_adaptive_instructions(account_name)
    print(f"💡 適応的指示:\n{json.dumps(instructions, ensure_ascii=False, indent=2)}")
