#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube動画文字起こしツール - 工程1B

このスクリプトは、YouTube動画のURLから字幕データを自動取得し、
講座作成のためのリサーチデータとして保存します。
"""

import argparse
import json
import sys
import re
from datetime import datetime
from typing import List, Dict, Optional

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
except ImportError as e:
    print(f"Error: Required library not found: {e}", file=sys.stderr)
    print("Please install required library:", file=sys.stderr)
    print("  pip3 install youtube-transcript-api", file=sys.stderr)
    sys.exit(1)


class YouTubeTranscriber:
    """YouTube動画の文字起こしを行うクラス"""

    def __init__(self, language_codes: List[str] = None):
        """
        初期化

        Args:
            language_codes: 取得する字幕の言語コードリスト（デフォルト: ['ja', 'en']）
        """
        self.language_codes = language_codes or ['ja', 'en']
        self.formatter = TextFormatter()

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        YouTube URLから動画IDを抽出

        Args:
            url: YouTube動画のURL

        Returns:
            動画ID（抽出できない場合はNone）
        """
        # 様々なYouTube URLフォーマットに対応
        patterns = [
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)',
            r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)',
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?]+)',
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([^?]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # URLではなく直接動画IDが渡された場合
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url

        return None

    def get_transcript(self, video_id: str) -> Optional[Dict]:
        """
        動画IDから字幕データを取得

        Args:
            video_id: YouTube動画ID

        Returns:
            字幕データの辞書（取得できない場合はNone）
        """
        try:
            print(f"  📹 動画ID: {video_id}")

            # YouTubeTranscriptApiをインスタンス化
            ytt_api = YouTubeTranscriptApi()

            # 字幕リストを取得
            transcript_list = ytt_api.list(video_id)

            # 字幕を取得（言語コードの優先順位で試行）
            transcript = None
            used_language = None

            # まず指定された言語で字幕を探す
            try:
                transcript = transcript_list.find_transcript(self.language_codes)
                used_language = transcript.language_code
                print(f"  ✓ 字幕を取得: {used_language}")
            except Exception as e:
                print(f"  - 指定言語で見つかりません: {str(e)[:50]}...")

                # 利用可能な字幕を表示
                available_langs = [t.language_code for t in transcript_list]
                print(f"  ℹ 利用可能な字幕: {', '.join(available_langs)}")

            if not transcript:
                print(f"  ✗ 字幕が見つかりません（対応言語: {', '.join(self.language_codes)}）", file=sys.stderr)
                return None

            # 字幕データを取得
            fetched_transcript = transcript.fetch()

            # スニペットのリストを取得
            snippets = list(fetched_transcript.snippets)

            # テキストを結合
            text = ' '.join([snippet.text for snippet in snippets])

            # 字幕の詳細情報を保持
            segments = []
            for snippet in snippets:
                segments.append({
                    'start': snippet.start,
                    'duration': snippet.duration,
                    'text': snippet.text
                })

            return {
                'video_id': video_id,
                'language': used_language,
                'text': text,
                'word_count': len(text),
                'segments': segments,
                'total_duration': segments[-1]['start'] + segments[-1]['duration'] if segments else 0
            }

        except Exception as e:
            print(f"  ✗ エラー: {e}", file=sys.stderr)
            return None

    def transcribe_videos(self, video_urls: List[str]) -> Dict:
        """
        複数の動画を文字起こし

        Args:
            video_urls: YouTube動画URLのリスト

        Returns:
            文字起こし結果の辞書
        """
        print("=" * 60)
        print("🎬 YouTube動画文字起こし - 工程1B")
        print("=" * 60)
        print(f"📋 対象動画数: {len(video_urls)}")

        results = []

        for i, url in enumerate(video_urls, 1):
            print(f"\n[{i}/{len(video_urls)}] 処理中...")
            print(f"  🔗 URL: {url[:60]}...")

            # 動画IDを抽出
            video_id = self.extract_video_id(url)
            if not video_id:
                print(f"  ✗ 無効なURL", file=sys.stderr)
                continue

            # 字幕を取得
            transcript = self.get_transcript(video_id)
            if transcript:
                transcript['source_url'] = url
                results.append(transcript)

        # 結果をまとめる
        transcription_data = {
            'transcription_date': datetime.now().isoformat(),
            'source_type': 'youtube',
            'total_videos': len(video_urls),
            'successful_transcriptions': len(results),
            'success_rate': f"{len(results)}/{len(video_urls)} ({len(results)/len(video_urls)*100:.1f}%)" if video_urls else "0/0",
            'transcriptions': results,
            'summary': {
                'total_words': sum(t['word_count'] for t in results),
                'total_duration': sum(t['total_duration'] for t in results),
                'average_words_per_video': sum(t['word_count'] for t in results) // len(results) if results else 0,
                'languages_used': list(set(t['language'] for t in results))
            }
        }

        return transcription_data

    def save_to_json(self, data: Dict, output_path: str):
        """
        データをJSON形式で保存

        Args:
            data: 保存するデータ
            output_path: 出力ファイルパス
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n💾 データを保存しました: {output_path}")
        except Exception as e:
            print(f"\n✗ 保存エラー: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='YouTube動画文字起こしツール - 講座作成のためのリサーチデータ収集'
    )

    # URLリスト方式と直接URL指定の選択
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--url-list',
        help='YouTube URLリストファイルのパス（1行に1URL）'
    )
    input_group.add_argument(
        '--urls',
        nargs='+',
        help='YouTube動画のURL（複数指定可）'
    )

    parser.add_argument(
        '--languages',
        nargs='+',
        default=['ja', 'en'],
        help='取得する字幕の言語コード（デフォルト: ja en）'
    )
    parser.add_argument(
        '--output',
        default='youtube_transcripts.json',
        help='出力JSONファイル名（デフォルト: youtube_transcripts.json）'
    )

    args = parser.parse_args()

    # URLリストを取得
    if args.url_list:
        try:
            with open(args.url_list, 'r', encoding='utf-8') as f:
                video_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

            if not video_urls:
                print("Error: URLリストが空です", file=sys.stderr)
                sys.exit(1)

        except FileNotFoundError:
            print(f"Error: ファイルが見つかりません: {args.url_list}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        video_urls = args.urls

    # 文字起こしを実行
    transcriber = YouTubeTranscriber(language_codes=args.languages)
    transcription_data = transcriber.transcribe_videos(video_urls)

    # 結果を保存
    transcriber.save_to_json(transcription_data, args.output)

    # サマリーを表示
    print("\n" + "=" * 60)
    print("📊 文字起こし完了サマリー")
    print("=" * 60)
    print(f"対象動画数: {transcription_data['total_videos']}")
    print(f"成功率: {transcription_data['success_rate']}")
    print(f"総文字数: {transcription_data['summary']['total_words']:,}文字")
    print(f"総再生時間: {transcription_data['summary']['total_duration']:.1f}秒 ({transcription_data['summary']['total_duration']/60:.1f}分)")

    if transcription_data['successful_transcriptions'] > 0:
        print(f"平均文字数: {transcription_data['summary']['average_words_per_video']:,}文字/動画")
        print(f"使用言語: {', '.join(transcription_data['summary']['languages_used'])}")

    print("=" * 60)


if __name__ == '__main__':
    main()
