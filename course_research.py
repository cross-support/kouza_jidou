#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
講座コンテンツ自動リサーチツール - 工程1A: Google検索によるネット情報収集

このスクリプトは、講座のテーマやキーワードから関連情報をWeb上から自動収集します。
ブログ自動化システムの工程5（一次情報追加）を参考に、講座作成向けにカスタマイズしています。
"""

import argparse
import json
import sys
import time
from datetime import datetime
from typing import List, Dict, Optional
import re

try:
    import requests
    from bs4 import BeautifulSoup
    from duckduckgo_search import DDGS
except ImportError as e:
    print(f"Error: Required library not found: {e}", file=sys.stderr)
    print("Please install required libraries:", file=sys.stderr)
    print("  pip3 install requests beautifulsoup4 duckduckgo-search", file=sys.stderr)
    sys.exit(1)


class CourseResearcher:
    """講座コンテンツのリサーチを行うクラス"""

    def __init__(self, keywords: List[str], num_results: int = 10):
        """
        初期化

        Args:
            keywords: 検索キーワードのリスト
            num_results: 取得する検索結果の数（デフォルト: 10）
        """
        self.keywords = keywords
        self.num_results = num_results
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.collected_data = []

    def search_duckduckgo(self, query: str) -> List[Dict[str, str]]:
        """
        DuckDuckGo検索を実行し、検索結果のURLとタイトルを取得

        Args:
            query: 検索クエリ

        Returns:
            検索結果のリスト [{'title': str, 'url': str, 'snippet': str}, ...]
        """
        print(f"\n🔍 DuckDuckGo検索: '{query}'")

        try:
            results = []

            # DuckDuckGo検索を実行
            with DDGS() as ddgs:
                search_results = ddgs.text(
                    query + " site:.jp OR site:.com",  # 日本語サイトと英語サイトを優先
                    region='jp-jp',
                    safesearch='moderate',
                    max_results=self.num_results
                )

                for result in search_results:
                    results.append({
                        'title': result.get('title', 'No title'),
                        'url': result.get('href', ''),
                        'snippet': result.get('body', '')
                    })

            print(f"  ✓ {len(results)}件の検索結果を取得")
            return results

        except Exception as e:
            print(f"  ✗ 検索エラー: {e}", file=sys.stderr)
            return []

    def extract_content(self, url: str) -> Optional[Dict[str, str]]:
        """
        指定URLからコンテンツを抽出

        Args:
            url: 対象URL

        Returns:
            抽出されたコンテンツ {'title': str, 'text': str, 'url': str}
        """
        try:
            print(f"  📄 コンテンツ取得: {url[:60]}...")

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 不要な要素を削除
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()

            # タイトルを取得
            title = soup.find('title')
            title_text = title.get_text().strip() if title else 'No title'

            # 本文を取得（article > main > body の順で試行）
            content = None
            for tag in ['article', 'main', 'body']:
                content = soup.find(tag)
                if content:
                    break

            if not content:
                content = soup

            # テキストを抽出
            text = content.get_text(separator='\n', strip=True)

            # 空白行を削除し、整形
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            cleaned_text = '\n'.join(lines)

            # 文字数制限（最大10000文字）
            if len(cleaned_text) > 10000:
                cleaned_text = cleaned_text[:10000] + '...'

            print(f"    ✓ {len(cleaned_text)}文字を抽出")

            return {
                'title': title_text,
                'url': url,
                'text': cleaned_text,
                'word_count': len(cleaned_text)
            }

        except Exception as e:
            print(f"    ✗ コンテンツ取得エラー: {e}", file=sys.stderr)
            return None

    def research_from_urls(self, url_list: List[str]) -> Dict:
        """
        URLリストからリサーチを実行

        Args:
            url_list: URLのリスト

        Returns:
            収集したデータの辞書
        """
        print("=" * 60)
        print("🎓 講座コンテンツ自動リサーチ - 工程1A（URLリスト方式）")
        print("=" * 60)
        print(f"📋 対象URL数: {len(url_list)}")

        all_results = []

        for i, url in enumerate(url_list, 1):
            print(f"\n[{i}/{len(url_list)}] 処理中...")

            # レート制限（1秒待機）
            if i > 1:
                time.sleep(1)

            content = self.extract_content(url)
            if content:
                all_results.append(content)

        # 結果をまとめる
        research_data = {
            'research_date': datetime.now().isoformat(),
            'source_type': 'url_list',
            'total_sources': len(all_results),
            'success_rate': f"{len(all_results)}/{len(url_list)} ({len(all_results)/len(url_list)*100:.1f}%)",
            'sources': all_results,
            'summary': {
                'total_words': sum(s['word_count'] for s in all_results),
                'unique_urls': len(set(s['url'] for s in all_results)),
                'average_words_per_source': sum(s['word_count'] for s in all_results) // len(all_results) if all_results else 0
            }
        }

        return research_data

    def research(self) -> Dict:
        """
        リサーチを実行（キーワード検索方式）

        Returns:
            収集したデータの辞書
        """
        print("=" * 60)
        print("🎓 講座コンテンツ自動リサーチ - 工程1A")
        print("=" * 60)

        all_results = []

        for keyword in self.keywords:
            # DuckDuckGo検索を実行
            search_results = self.search_duckduckgo(keyword)

            # 各検索結果からコンテンツを抽出
            for result in search_results:
                # レート制限（1秒待機）
                time.sleep(1)

                content = self.extract_content(result['url'])
                if content:
                    content['search_keyword'] = keyword
                    content['search_snippet'] = result['snippet']
                    all_results.append(content)

        # 結果をまとめる
        research_data = {
            'research_date': datetime.now().isoformat(),
            'source_type': 'keyword_search',
            'keywords': self.keywords,
            'total_sources': len(all_results),
            'sources': all_results,
            'summary': {
                'total_words': sum(s['word_count'] for s in all_results),
                'unique_urls': len(set(s['url'] for s in all_results))
            }
        }

        return research_data

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
        description='講座コンテンツ自動リサーチツール - Web情報収集'
    )

    # URLリスト方式とキーワード検索方式の選択
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--url-list',
        help='URLリストファイルのパス（1行に1URL）'
    )
    input_group.add_argument(
        '--keywords',
        nargs='+',
        help='検索キーワード（複数指定可）例: "ChatGPT 業務活用" "AI 活用事例"'
    )

    parser.add_argument(
        '--num-results',
        type=int,
        default=10,
        help='各キーワードで取得する検索結果の数（デフォルト: 10）※キーワード検索時のみ'
    )
    parser.add_argument(
        '--output',
        default='course_research_output.json',
        help='出力JSONファイル名（デフォルト: course_research_output.json）'
    )

    args = parser.parse_args()

    # URLリスト方式
    if args.url_list:
        try:
            with open(args.url_list, 'r', encoding='utf-8') as f:
                url_list = [line.strip() for line in f if line.strip() and not line.startswith('#')]

            if not url_list:
                print("Error: URLリストが空です", file=sys.stderr)
                sys.exit(1)

            researcher = CourseResearcher(keywords=[], num_results=0)
            research_data = researcher.research_from_urls(url_list)

        except FileNotFoundError:
            print(f"Error: ファイルが見つかりません: {args.url_list}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # キーワード検索方式
    else:
        researcher = CourseResearcher(
            keywords=args.keywords,
            num_results=args.num_results
        )
        research_data = researcher.research()

    # 結果を保存
    researcher.save_to_json(research_data, args.output)

    # サマリーを表示
    print("\n" + "=" * 60)
    print("📊 リサーチ完了サマリー")
    print("=" * 60)

    if args.url_list:
        print(f"入力方式: URLリスト ({args.url_list})")
        print(f"成功率: {research_data['success_rate']}")
    else:
        print(f"入力方式: キーワード検索")
        print(f"検索キーワード数: {len(args.keywords)}")

    print(f"取得ソース数: {research_data['total_sources']}")
    print(f"総文字数: {research_data['summary']['total_words']:,}文字")
    print(f"ユニークURL数: {research_data['summary']['unique_urls']}")

    if args.url_list and research_data['total_sources'] > 0:
        print(f"平均文字数: {research_data['summary']['average_words_per_source']:,}文字/ソース")

    print("=" * 60)


if __name__ == '__main__':
    main()
