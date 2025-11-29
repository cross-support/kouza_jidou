#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合リサーチツール - 工程1A + 1B

このスクリプトは、Webリサーチ（工程1A）とYouTube文字起こし（工程1B）を
1つのコマンドで実行し、講座作成のための包括的なリサーチデータを収集します。
"""

import argparse
import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class UnifiedResearchTool:
    """統合リサーチツール"""

    def __init__(self):
        self.script_dir = Path(__file__).parent

    def run_web_research(self, url_list: str, output: str) -> Optional[Dict]:
        """
        Webリサーチを実行（工程1A）

        Args:
            url_list: WebのURLリストファイル
            output: 出力JSONファイル名

        Returns:
            リサーチ結果の辞書（失敗時はNone）
        """
        print("=" * 60)
        print("📚 工程1A: Webリサーチを開始")
        print("=" * 60)

        script_path = self.script_dir / "course_research.py"

        if not script_path.exists():
            print(f"✗ エラー: course_research.py が見つかりません", file=sys.stderr)
            return None

        try:
            # course_research.py を実行
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    "--url-list", url_list,
                    "--output", output
                ],
                capture_output=True,
                text=True,
                check=True
            )

            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            # 生成されたJSONファイルを読み込み
            with open(output, 'r', encoding='utf-8') as f:
                return json.load(f)

        except subprocess.CalledProcessError as e:
            print(f"✗ Webリサーチ実行エラー: {e}", file=sys.stderr)
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr, file=sys.stderr)
            return None
        except FileNotFoundError as e:
            print(f"✗ ファイル読み込みエラー: {e}", file=sys.stderr)
            return None
        except json.JSONDecodeError as e:
            print(f"✗ JSON解析エラー: {e}", file=sys.stderr)
            return None

    def run_youtube_research(self, url_list: str, output: str, languages: list = None) -> Optional[Dict]:
        """
        YouTube文字起こしを実行（工程1B）

        Args:
            url_list: YouTubeのURLリストファイル
            output: 出力JSONファイル名
            languages: 字幕言語コードのリスト

        Returns:
            文字起こし結果の辞書（失敗時はNone）
        """
        print("\n" + "=" * 60)
        print("🎥 工程1B: YouTube文字起こしを開始")
        print("=" * 60)

        script_path = self.script_dir / "youtube_transcriber.py"

        if not script_path.exists():
            print(f"✗ エラー: youtube_transcriber.py が見つかりません", file=sys.stderr)
            return None

        try:
            # youtube_transcriber.py を実行
            cmd = [
                sys.executable,
                str(script_path),
                "--url-list", url_list,
                "--output", output
            ]

            if languages:
                cmd.extend(["--languages"] + languages)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            # 生成されたJSONファイルを読み込み
            with open(output, 'r', encoding='utf-8') as f:
                return json.load(f)

        except subprocess.CalledProcessError as e:
            print(f"✗ YouTube文字起こし実行エラー: {e}", file=sys.stderr)
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr, file=sys.stderr)
            return None
        except FileNotFoundError as e:
            print(f"✗ ファイル読み込みエラー: {e}", file=sys.stderr)
            return None
        except json.JSONDecodeError as e:
            print(f"✗ JSON解析エラー: {e}", file=sys.stderr)
            return None

    def generate_summary(self, web_data: Optional[Dict], youtube_data: Optional[Dict]) -> Dict:
        """
        統合サマリーを生成

        Args:
            web_data: Webリサーチデータ
            youtube_data: YouTube文字起こしデータ

        Returns:
            統合サマリーの辞書
        """
        summary = {
            'unified_research_date': datetime.now().isoformat(),
            'web_research': {
                'status': 'success' if web_data else 'failed',
                'sources': web_data.get('total_sources', 0) if web_data else 0,
                'characters': web_data.get('summary', {}).get('total_characters', 0) if web_data else 0
            },
            'youtube_research': {
                'status': 'success' if youtube_data else 'failed',
                'videos': youtube_data.get('successful_transcriptions', 0) if youtube_data else 0,
                'characters': youtube_data.get('summary', {}).get('total_words', 0) if youtube_data else 0,
                'duration_minutes': youtube_data.get('summary', {}).get('total_duration', 0) / 60 if youtube_data else 0
            },
            'total': {
                'total_sources': (
                    (web_data.get('total_sources', 0) if web_data else 0) +
                    (youtube_data.get('successful_transcriptions', 0) if youtube_data else 0)
                ),
                'total_characters': (
                    (web_data.get('summary', {}).get('total_characters', 0) if web_data else 0) +
                    (youtube_data.get('summary', {}).get('total_words', 0) if youtube_data else 0)
                )
            }
        }
        return summary

    def print_summary(self, summary: Dict):
        """サマリーを表示"""
        print("\n" + "=" * 60)
        print("📊 統合リサーチ完了サマリー")
        print("=" * 60)

        # Webリサーチ
        web = summary['web_research']
        status_icon = "✓" if web['status'] == 'success' else "✗"
        print(f"\n📚 Webリサーチ: {status_icon} {web['status'].upper()}")
        if web['status'] == 'success':
            print(f"  - 情報源: {web['sources']}件")
            print(f"  - 文字数: {web['characters']:,}文字")

        # YouTube文字起こし
        youtube = summary['youtube_research']
        status_icon = "✓" if youtube['status'] == 'success' else "✗"
        print(f"\n🎥 YouTube文字起こし: {status_icon} {youtube['status'].upper()}")
        if youtube['status'] == 'success':
            print(f"  - 動画数: {youtube['videos']}件")
            print(f"  - 文字数: {youtube['characters']:,}文字")
            print(f"  - 総再生時間: {youtube['duration_minutes']:.1f}分")

        # 合計
        total = summary['total']
        print(f"\n📈 合計:")
        print(f"  - 総情報源: {total['total_sources']}件")
        print(f"  - 総文字数: {total['total_characters']:,}文字")

        print("=" * 60)

    def save_summary(self, summary: Dict, output_path: str):
        """サマリーをJSONファイルとして保存"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            print(f"\n💾 統合サマリーを保存: {output_path}")
        except Exception as e:
            print(f"✗ サマリー保存エラー: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='統合リサーチツール - Webリサーチ + YouTube文字起こしを一括実行'
    )

    # 入力ファイル
    parser.add_argument(
        '--web-urls',
        help='WebのURLリストファイル（省略可：Webリサーチをスキップ）'
    )
    parser.add_argument(
        '--youtube-urls',
        help='YouTubeのURLリストファイル（省略可：YouTube文字起こしをスキップ）'
    )

    # 出力ファイル
    parser.add_argument(
        '--web-output',
        default='web_research.json',
        help='Webリサーチの出力JSONファイル名（デフォルト: web_research.json）'
    )
    parser.add_argument(
        '--youtube-output',
        default='youtube_transcripts.json',
        help='YouTube文字起こしの出力JSONファイル名（デフォルト: youtube_transcripts.json）'
    )
    parser.add_argument(
        '--summary-output',
        default='research_summary.json',
        help='統合サマリーの出力JSONファイル名（デフォルト: research_summary.json）'
    )

    # YouTube字幕言語
    parser.add_argument(
        '--languages',
        nargs='+',
        default=['ja', 'en'],
        help='YouTube字幕の言語コード（デフォルト: ja en）'
    )

    args = parser.parse_args()

    # 少なくとも1つの入力が必要
    if not args.web_urls and not args.youtube_urls:
        parser.error("--web-urls または --youtube-urls のいずれかを指定してください")

    tool = UnifiedResearchTool()

    print("=" * 60)
    print("🚀 統合リサーチツール - 工程1A + 1B")
    print("=" * 60)
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Webリサーチを実行
    web_data = None
    if args.web_urls:
        web_data = tool.run_web_research(args.web_urls, args.web_output)
    else:
        print("📚 Webリサーチをスキップ（--web-urls が指定されていません）\n")

    # YouTube文字起こしを実行
    youtube_data = None
    if args.youtube_urls:
        youtube_data = tool.run_youtube_research(
            args.youtube_urls,
            args.youtube_output,
            args.languages
        )
    else:
        print("🎥 YouTube文字起こしをスキップ（--youtube-urls が指定されていません）\n")

    # サマリーを生成・表示・保存
    summary = tool.generate_summary(web_data, youtube_data)
    tool.print_summary(summary)
    tool.save_summary(summary, args.summary_output)

    # 次のステップの案内
    print("\n" + "=" * 60)
    print("📝 次のステップ:")
    print("=" * 60)
    print("以下のコマンドで講座生成プロンプトを作成できます:\n")

    cmd_parts = [
        "python3 course_plan_parser.py",
        '  --csv "自動R7.11 講座計画表.csv"',
        '  --course "講座名"',
        '  --format canvas-script',
        '  --learner_profile "受講者像"',
        '  --target_behavior "到達目標"',
        '  --duration "30分"',
        '  --tone "トーン"'
    ]

    if web_data:
        cmd_parts.append(f'  --web-research "{args.web_output}"')
    if youtube_data:
        cmd_parts.append(f'  --youtube-research "{args.youtube_output}"')

    cmd_parts.append('  > gemini_prompt.txt')

    print(" \\\n".join(cmd_parts))
    print("\n" + "=" * 60)

    # 終了コードを設定
    if not web_data and not youtube_data:
        sys.exit(1)  # 両方失敗
    elif (args.web_urls and not web_data) or (args.youtube_urls and not youtube_data):
        sys.exit(2)  # 部分的に失敗
    else:
        sys.exit(0)  # 成功


if __name__ == '__main__':
    main()
