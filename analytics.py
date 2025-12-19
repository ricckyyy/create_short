#!/usr/bin/env python3
"""
アナリティクス・分析モジュール
再生数データから成功パターンを分析し、次の台本生成に活用
"""

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from db_manager import get_connection, get_top_videos, get_all_videos


def analyze_successful_scripts(account_name, top_n=10):
    """
    成功した動画の台本を分析してパターンを抽出
    
    Args:
        account_name: アカウント名
        top_n: 分析する上位動画数
    
    Returns:
        dict: 成功パターンの分析結果
    """
    # 再生数上位の動画を取得
    top_videos = get_top_videos(account_name, limit=top_n, order_by="views")
    
    if not top_videos:
        return {
            "status": "no_data",
            "message": "分析に十分なデータがありません"
        }
    
    # 分析結果
    analysis = {
        "account_name": account_name,
        "sample_count": len(top_videos),
        "avg_views": sum(v["views"] for v in top_videos) / len(top_videos),
        "opening_patterns": analyze_openings(top_videos),
        "content_length": analyze_content_length(top_videos),
        "keyword_frequency": analyze_keywords(top_videos),
        "cta_patterns": analyze_cta(top_videos),
        "successful_scripts": [
            {
                "title": v["title"],
                "views": v["views"],
                "script": v["script_content"][:100] + "..."  # 最初の100文字
            }
            for v in top_videos[:3]  # 上位3つ
        ]
    }
    
    return analysis


def analyze_openings(videos):
    """冒頭パターンを分析"""
    openings = []
    
    for video in videos:
        script = video["script_content"]
        lines = [line.strip() for line in script.split("\n") if line.strip()]
        if lines:
            first_line = lines[0]
            openings.append({
                "text": first_line[:50],  # 最初の50文字
                "views": video["views"],
                "length": len(first_line)
            })
    
    # パターン分類
    question_pattern = sum(1 for o in openings if "？" in o["text"] or "?" in o["text"])
    exclamation_pattern = sum(1 for o in openings if "！" in o["text"] or "!" in o["text"])
    
    avg_length = sum(o["length"] for o in openings) / len(openings) if openings else 0
    
    return {
        "question_rate": question_pattern / len(openings) if openings else 0,
        "exclamation_rate": exclamation_pattern / len(openings) if openings else 0,
        "avg_first_line_length": avg_length,
        "top_openings": sorted(openings, key=lambda x: x["views"], reverse=True)[:3]
    }


def analyze_content_length(videos):
    """コンテンツ長を分析"""
    lengths = []
    
    for video in videos:
        script = video["script_content"]
        lines = [line.strip() for line in script.split("\n") if line.strip()]
        lengths.append({
            "line_count": len(lines),
            "char_count": len(script),
            "views": video["views"]
        })
    
    avg_lines = sum(l["line_count"] for l in lengths) / len(lengths) if lengths else 0
    avg_chars = sum(l["char_count"] for l in lengths) / len(lengths) if lengths else 0
    
    # 最高再生数の動画の長さ
    best = max(lengths, key=lambda x: x["views"]) if lengths else None
    
    return {
        "avg_lines": avg_lines,
        "avg_chars": avg_chars,
        "best_performing": best
    }


def analyze_keywords(videos):
    """キーワードの頻出度を分析"""
    all_keywords = []
    
    for video in videos:
        if video.get("keywords"):
            try:
                keywords = json.loads(video["keywords"]) if isinstance(video["keywords"], str) else video["keywords"]
                if keywords:
                    all_keywords.extend(keywords)
            except:
                pass
    
    # 頻出キーワード
    keyword_counter = Counter(all_keywords)
    top_keywords = keyword_counter.most_common(10)
    
    return {
        "total_unique_keywords": len(set(all_keywords)),
        "top_keywords": [{"keyword": k, "count": c} for k, c in top_keywords]
    }


def analyze_cta(videos):
    """CTA（行動喚起）パターンを分析"""
    cta_patterns = []
    
    for video in videos:
        script = video["script_content"]
        lines = [line.strip() for line in script.split("\n") if line.strip()]
        if lines:
            last_line = lines[-1]
            
            # CTAキーワード検出
            has_follow = "フォロー" in last_line or "follow" in last_line.lower()
            has_comment = "コメント" in last_line or "comment" in last_line.lower()
            has_like = "いいね" in last_line or "like" in last_line.lower()
            
            cta_patterns.append({
                "text": last_line[:50],
                "has_follow": has_follow,
                "has_comment": has_comment,
                "has_like": has_like,
                "views": video["views"]
            })
    
    # 効果的なCTA判定
    follow_ctas = [c for c in cta_patterns if c["has_follow"]]
    comment_ctas = [c for c in cta_patterns if c["has_comment"]]
    
    avg_follow_views = sum(c["views"] for c in follow_ctas) / len(follow_ctas) if follow_ctas else 0
    avg_comment_views = sum(c["views"] for c in comment_ctas) / len(comment_ctas) if comment_ctas else 0
    
    return {
        "follow_cta_count": len(follow_ctas),
        "comment_cta_count": len(comment_ctas),
        "avg_follow_views": avg_follow_views,
        "avg_comment_views": avg_comment_views,
        "top_ctas": sorted(cta_patterns, key=lambda x: x["views"], reverse=True)[:3]
    }


def generate_insights(account_name):
    """
    分析結果から実用的なインサイトを生成
    
    Returns:
        list: インサイト文のリスト
    """
    analysis = analyze_successful_scripts(account_name)
    
    if analysis.get("status") == "no_data":
        return ["データが不足しています。動画を生成して再生数を記録してください。"]
    
    insights = []
    
    # 冒頭パターンのインサイト
    if analysis["opening_patterns"]["question_rate"] > 0.5:
        insights.append("✅ 疑問形で始まる動画の再生数が高い傾向")
    
    # 長さのインサイト
    best_length = analysis["content_length"]["best_performing"]
    if best_length:
        insights.append(f"✅ 最高再生数の動画は{best_length['line_count']}行構成")
    
    # キーワードのインサイト
    top_keywords = analysis["keyword_frequency"]["top_keywords"][:3]
    if top_keywords:
        keywords_str = "、".join([k["keyword"] for k in top_keywords])
        insights.append(f"✅ 効果的なキーワード: {keywords_str}")
    
    # CTAのインサイト
    if analysis["cta_patterns"]["avg_follow_views"] > analysis["avg_views"]:
        insights.append("✅ 'フォロー'促進CTAが効果的")
    
    if analysis["cta_patterns"]["avg_comment_views"] > analysis["avg_views"]:
        insights.append("✅ 'コメント'促進CTAが効果的")
    
    return insights


def save_analysis_report(account_name, output_dir="data/analytics/reports"):
    """分析レポートをJSONファイルとして保存"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    analysis = analyze_successful_scripts(account_name)
    insights = generate_insights(account_name)
    
    report = {
        "account_name": account_name,
        "generated_at": datetime.now().isoformat(),
        "analysis": analysis,
        "insights": insights
    }
    
    filename = output_path / f"analysis_{account_name}_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return filename


if __name__ == "__main__":
    # テスト: 心理テストラボの分析
    print("📊 アナリティクス分析テスト\n")
    
    account_name = "心理テストラボ"
    
    print(f"🔍 {account_name} を分析中...\n")
    analysis = analyze_successful_scripts(account_name, top_n=5)
    
    if analysis.get("status") == "no_data":
        print("⚠️ データがありません")
    else:
        print(f"✅ サンプル数: {analysis['sample_count']}")
        print(f"📈 平均再生数: {analysis['avg_views']:.0f}")
        print(f"📝 平均行数: {analysis['content_length']['avg_lines']:.1f}")
        print()
        
        print("💡 インサイト:")
        insights = generate_insights(account_name)
        for insight in insights:
            print(f"  {insight}")
        print()
        
        # レポート保存
        report_file = save_analysis_report(account_name)
        print(f"📄 レポート保存: {report_file}")
