import argparse
import pandas as pd
import json
import sys
from typing import Optional, Dict

def parse_course_plan(csv_path, course_name, unit_number=None):
    """CSVから特定の講座の情報を抽出する"""
    try:
        df = pd.read_csv(csv_path, header=0, usecols=range(6), dtype=str)
        df.columns = ['category', 'course', 'unit_no', 'unit_name', 'slide_no', 'slide_title']
        df = df.dropna(subset=['course', 'slide_title'])
        df = df[df['course'] != '講座名']
    except (FileNotFoundError, ValueError) as e:
        print(f"Error reading or parsing CSV: {e}", file=sys.stderr)
        sys.exit(1)

    course_df = df[df['course'] == course_name].copy()
    if course_df.empty:
        all_courses = df['course'].unique()
        similar_courses = [c for c in all_courses if course_name.lower() in c.lower()]
        print(f"Error: Course '{course_name}' not found.", file=sys.stderr)
        if similar_courses:
            print(f"Did you mean one of these? {', '.join(similar_courses)}", file=sys.stderr)
        sys.exit(1)

    if unit_number:
        # 複数ユニット対応: カンマ区切りで複数指定可能 (例: "1,2,3,4")
        unit_numbers = [u.strip() for u in str(unit_number).split(',')]
        course_df = course_df[course_df['unit_no'].isin(unit_numbers)]
        if course_df.empty:
            print(f"Error: Units '{unit_number}' not found for course '{course_name}'.", file=sys.stderr)
            available_units = df[df['course'] == course_name]['unit_no'].unique()
            print(f"Available units: {', '.join(map(str, sorted(available_units)))}", file=sys.stderr)
            sys.exit(1)
    
    course_df['unit_no'] = pd.to_numeric(course_df['unit_no'])
    course_df['slide_no'] = pd.to_numeric(course_df['slide_no'])
    course_df = course_df.sort_values(by=['unit_no', 'slide_no'])

    return course_df

def load_research_data(json_path: str) -> Optional[Dict]:
    """リサーチデータJSONファイルを読み込む"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Research file not found: {json_path}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in research file: {json_path} - {e}", file=sys.stderr)
        return None

def format_web_research(research_data: Dict) -> str:
    """Webリサーチデータをプロンプト用にフォーマット"""
    if not research_data or not research_data.get('sources'):
        return ""

    output = ["### 📚 Web リサーチデータ"]
    output.append(f"- 収集日: {research_data.get('research_date', 'N/A')}")
    output.append(f"- 情報源数: {research_data.get('total_sources', 0)}件")
    output.append(f"- 総文字数: {research_data.get('summary', {}).get('total_characters', 0):,}文字\n")

    for i, source in enumerate(research_data.get('sources', [])[:5], 1):  # 最大5件まで表示
        output.append(f"**情報源{i}: {source.get('title', 'タイトルなし')}**")
        output.append(f"- URL: {source.get('url', 'N/A')}")
        output.append(f"- 文字数: {source.get('character_count', 0):,}文字")

        # コンテンツの要約（最初の500文字）
        content = source.get('content', '')
        if content:
            preview = content[:500] + "..." if len(content) > 500 else content
            output.append(f"- 内容抜粋: {preview}\n")

    if len(research_data.get('sources', [])) > 5:
        remaining = len(research_data.get('sources', [])) - 5
        output.append(f"（他{remaining}件の情報源を省略）\n")

    return "\n".join(output)

def format_youtube_research(research_data: Dict) -> str:
    """YouTube文字起こしデータをプロンプト用にフォーマット"""
    if not research_data or not research_data.get('transcriptions'):
        return ""

    output = ["### 🎥 YouTube 文字起こしデータ"]
    output.append(f"- 文字起こし日: {research_data.get('transcription_date', 'N/A')}")
    output.append(f"- 動画数: {research_data.get('successful_transcriptions', 0)}件")
    output.append(f"- 総文字数: {research_data.get('summary', {}).get('total_words', 0):,}文字")
    output.append(f"- 総再生時間: {research_data.get('summary', {}).get('total_duration', 0)/60:.1f}分\n")

    for i, transcript in enumerate(research_data.get('transcriptions', [])[:3], 1):  # 最大3件まで表示
        output.append(f"**動画{i}: {transcript.get('video_id', 'N/A')}**")
        output.append(f"- URL: {transcript.get('source_url', 'N/A')}")
        output.append(f"- 言語: {transcript.get('language', 'N/A')}")
        output.append(f"- 文字数: {transcript.get('word_count', 0):,}文字")
        output.append(f"- 動画時間: {transcript.get('total_duration', 0)/60:.1f}分")

        # 文字起こしテキストの要約（最初の800文字）
        text = transcript.get('text', '')
        if text:
            preview = text[:800] + "..." if len(text) > 800 else text
            output.append(f"- 内容抜粋: {preview}\n")

    if len(research_data.get('transcriptions', [])) > 3:
        remaining = len(research_data.get('transcriptions', [])) - 3
        output.append(f"（他{remaining}件の動画を省略）\n")

    return "\n".join(output)

def format_quality_assurance(quality_report: Dict, terminology_report: Dict) -> str:
    """品質保証レポートをプロンプト用にフォーマット"""
    if not quality_report and not terminology_report:
        return ""

    output = ["### 🔍 品質保証データ（講座作成の指針）"]
    output.append("以下の品質分析結果を参考に、正確で教育的価値の高いコンテンツを作成してください。\n")

    # 品質検証レポート
    if quality_report:
        overall_quality = quality_report.get('overall_quality', 'unknown')
        quality_labels = {
            'excellent': '優秀',
            'good': '良好',
            'acceptable': '許容範囲',
            'needs_improvement': '改善必要'
        }
        quality_label = quality_labels.get(overall_quality, '不明')

        output.append(f"**品質評価**: {quality_label}")

        summary = quality_report.get('integrated_summary', {})
        output.append(f"- データポイント数: {summary.get('total_data_points', 0)}件")
        output.append(f"- 信頼性の高い情報源: {summary.get('credible_sources', 0)}件")

        # 推奨事項（最初の3件）
        recommendations = quality_report.get('quality_recommendations', [])[:3]
        if recommendations:
            output.append("\n**品質に関する注意点**:")
            for rec in recommendations:
                output.append(f"- {rec}")

    # 用語分析レポート
    if terminology_report:
        summary = terminology_report.get('terminology_summary', {})
        output.append(f"\n**重要用語分析**:")
        output.append(f"- 検出された重要用語数: {summary.get('total_unique_terms', 0)}個")

        # カテゴリ分布
        categories = summary.get('categories', {})
        if categories:
            cat_str = ', '.join([f"{k}: {v}個" for k, v in categories.items()])
            output.append(f"- カテゴリ分布: {cat_str}")

        # 学習フェーズ分布
        phases = summary.get('learning_phases', {})
        if phases:
            phase_labels = {
                'introduction': '導入',
                'understanding': '理解',
                'application': '実践'
            }
            phase_str = ', '.join([f"{phase_labels.get(k, k)}: {v}個" for k, v in phases.items()])
            output.append(f"- 学習フェーズ分布: {phase_str}")

        # トップ10用語
        top_terms = terminology_report.get('top_terms', [])[:10]
        if top_terms:
            terms_list = [term['term'] for term in top_terms]
            output.append(f"\n**必ず解説すべき重要用語トップ10**:")
            output.append(f"{', '.join(terms_list)}")
            output.append("\n→ これらの用語は講座内で明確に定義し、適切に解説してください。")

        # 推奨事項（最初の2件）
        recommendations = terminology_report.get('recommendations', [])[:2]
        if recommendations:
            output.append("\n**用語に関する推奨事項**:")
            for rec in recommendations:
                output.append(f"- {rec}")

    output.append("")  # 空行
    return "\n".join(output)

def format_as_prompt(df, course_name):
    """LLMへのプロンプト形式で講座構成を出力"""
    if df.empty:
        return f"# {course_name}\n\n（この講座にはスライドが見つかりませんでした）"
    output = [f"## 講座名: {course_name}\n"]
    for unit_no, group in df.groupby('unit_no'):
        unit_name = group['unit_name'].iloc[0]
        output.append(f"### ユニット{int(unit_no)}: {unit_name}")
        for record in group.to_dict('records'):
            output.append(f"- スライド{record['slide_no']}: {record['slide_title']}")
    return "\n".join(output)

def format_as_canvas_and_narration_prompt(df, args, web_research_data=None, youtube_research_data=None, quality_report=None, terminology_report=None):
    """GeminiにCanvas用設計図とナレーション台本を一度に生成させるための指示書を生成"""
    structure_prompt = format_as_prompt(df, args.course)

    # リサーチデータのフォーマット
    research_section = ""
    if web_research_data or youtube_research_data:
        research_parts = []
        research_parts.append("# 📊 事前リサーチデータ（講座作成の参考情報）")
        research_parts.append("以下のリサーチデータは、講座内容をより正確で実践的なものにするための参考資料です。")
        research_parts.append("これらの情報を活用して、最新かつ信頼性の高いコンテンツを作成してください。\n")

        if web_research_data:
            web_formatted = format_web_research(web_research_data)
            if web_formatted:
                research_parts.append(web_formatted)

        if youtube_research_data:
            youtube_formatted = format_youtube_research(youtube_research_data)
            if youtube_formatted:
                research_parts.append(youtube_formatted)

        # 品質保証データを追加
        qa_formatted = format_quality_assurance(quality_report, terminology_report)
        if qa_formatted:
            research_parts.append(qa_formatted)

        research_parts.append("---\n")
        research_section = "\n".join(research_parts)

    canvas_prompt = f"""
あなたは、eラーニング講座の「インストラクショナルデザイナー」「ビジュアルデザイナー」「ナレーター」を兼務する専門家です。
これから、講座のコンテンツパッケージを、指定された2つのパートに分けて生成してください。

# 講座の全体仕様
- **講座テーマ**: {args.course}
- **受講者像**: {args.learner_profile}
- **到達目標（ゴール行動）**: {args.target_behavior}
- **想定時間**: {args.duration}
- **トーン＆マナー**: {args.tone}

# 生成対象の講座構成（この構成を厳守してください）
---
{structure_prompt}
---

{research_section}# あなたのタスク
以下の「パート1」と「パート2」を、この順番で、両方とも生成してください。

---
## パート1：Gemini Canvas用・ビジュアルスライド設計図

下記のフォーマットに従い、全スライドの視覚的な設計図をMarkdownで記述してください。これは、デザイナーやGeminiのCanvasモードがスライドを視覚的に作成するための指示書となります。モダンで分かりやすいデザインを心がけてください。

### ユニット [ユニット番号]: [ユニット名]

**スライド [スライド番号]: [スライドタイトル]**
- **レイアウト**: スライド全体の構成を指示します。（例：「タイトルを上部に配置し、中央に大きなアイコンを配置する」「左に画像、右に3つの箇条書きテキスト」）
- **キービジュアル**: 中心となるグラフィック要素を具体的に指示します。（例：「シンプルな電球のアイコン」「データを保護するイメージの抽象的なイラスト」「ChatGPTのプロンプト入力画面のスクリーンショット」）
- **スライド内テキスト**: スライドに表示するテキストを正確に記述します。タイトル以外は、3〜5行の短い箇条書きやキーワードに留め、シンプルにしてください。
- **推奨カラー**: スライドの基調となる色を2〜3色提案します。（例：「基調は落ち着いた青(#3366CC)、強調色にオレンジ(#FF8C00)」）

---
## パート2：タイムスタンプ付きナレーション・字幕台本

講座のナレーションと、動画用の字幕を生成します。下記のフォーマットに従い、Markdownのテーブル形式で出力してください。

### 台本作成の重要ルール
1.  **時間計算**: ナレーションの速度を「分速150ワード（1秒あたり2.5ワード）」と仮定し、ナレーションの単語数から各ブロックの「開始時間」と「終了時間」を計算してください。
2.  **字幕の分割**: 「ナレーション全文」を、意味が通じる単位で短いブロックに分割し、「字幕テキスト」を作成してください。字幕は**必ず2行以内**に収めてください。
3.  **タイムスタンプ形式**: 時間は `MM:SS` 形式（例: `00:08`, `02:15`）で記述してください。
4.  **情報セキュリティの強調**: この講座では、個人情報や社内の機密情報をChatGPTに入力しないことの重要性を、時間を割いて明確かつ強力に伝えてください。そのためのナレーションを必ず含めてください。

### 出力フォーマット（Markdownテーブル）

| スライド番号 | 開始時間 | 終了時間 | 字幕テキスト（最大2行） | ナレーション全文（口語体） |
|---|---|---|---|---|---|n| 1 | 00:00 | 00:05 | こんにちは！本日は「ChatGPT業務活用の基本」<br>について学んでいきましょう。 | こんにちは！本日は「ChatGPT業務活用の基本」について、皆さんと一緒に学んでいきましょう。 |
| 1 | 00:06 | 00:10 | この講座を終える頃には、<br>明日から使えるスキルが身についています。| この講座を終える頃には、皆さんの業務がもっと効率的になる、明日からすぐに使えるスキルが身についていますよ。 |
| ... | ... | ... | ... | ... |

"""
    return canvas_prompt

def main():
    parser = argparse.ArgumentParser(description="Parse course plan CSV and generate structured output for course creation.")
    parser.add_argument("--csv", required=True, help="Path to the course plan CSV file.")
    parser.add_argument("--course", required=True, help="The name of the course to extract.")
    parser.add_argument("--unit", help="(Optional) Specific unit number to filter by.")
    parser.add_argument(
        "--format",
        required=True,
        choices=["canvas-script"], # Kept as a single choice for now
        help="Output format. 'canvas-script' generates a full prompt for Gemini to create slide designs and a timed narration script.",
    )
    # Arguments for the prompt
    parser.add_argument("--learner_profile", required=True, help="Who the learners are.")
    parser.add_argument("--target_behavior", required=True, help="What learners should be able to do.")
    parser.add_argument("--duration", required=True, help="Estimated duration of the course.")
    parser.add_argument("--tone", required=True, help="Tone and manner of the course.")

    # 工程1A/1B リサーチデータの読み込み（オプション）
    parser.add_argument("--web-research", help="(Optional) Path to web research JSON file (from course_research.py).")
    parser.add_argument("--youtube-research", help="(Optional) Path to YouTube transcription JSON file (from youtube_transcriber.py).")

    # 工程1C/1D 品質保証データの読み込み（オプション）
    parser.add_argument("--quality-report", help="(Optional) Path to quality validation report JSON file (from course_quality_validator.py).")
    parser.add_argument("--terminology-report", help="(Optional) Path to terminology analysis report JSON file (from course_terminology_analyzer.py).")

    args = parser.parse_args()

    df = parse_course_plan(args.csv, args.course, args.unit)

    # リサーチデータを読み込み（指定されている場合）
    web_research_data = None
    youtube_research_data = None

    if args.web_research:
        print(f"📚 Webリサーチデータを読み込み中: {args.web_research}", file=sys.stderr)
        web_research_data = load_research_data(args.web_research)
        if web_research_data:
            print(f"  ✓ {web_research_data.get('total_sources', 0)}件の情報源を読み込みました", file=sys.stderr)

    if args.youtube_research:
        print(f"🎥 YouTube文字起こしデータを読み込み中: {args.youtube_research}", file=sys.stderr)
        youtube_research_data = load_research_data(args.youtube_research)
        if youtube_research_data:
            print(f"  ✓ {youtube_research_data.get('successful_transcriptions', 0)}件の動画を読み込みました", file=sys.stderr)

    # 品質保証データを読み込み（指定されている場合）
    quality_report = None
    terminology_report = None

    if args.quality_report:
        print(f"🔍 品質検証レポートを読み込み中: {args.quality_report}", file=sys.stderr)
        quality_report = load_research_data(args.quality_report)
        if quality_report:
            quality = quality_report.get('overall_quality', 'unknown')
            print(f"  ✓ 品質評価: {quality}", file=sys.stderr)

    if args.terminology_report:
        print(f"📖 用語分析レポートを読み込み中: {args.terminology_report}", file=sys.stderr)
        terminology_report = load_research_data(args.terminology_report)
        if terminology_report:
            term_count = terminology_report.get('terminology_summary', {}).get('total_unique_terms', 0)
            print(f"  ✓ {term_count}個の重要用語を検出", file=sys.stderr)

    if args.format == 'canvas-script':
        output = format_as_canvas_and_narration_prompt(df, args, web_research_data, youtube_research_data, quality_report, terminology_report)
    else:
        # Fallback, though argparse should prevent this.
        parser.error(f"Invalid format specified.")

    print(output)

if __name__ == "__main__":
    main()