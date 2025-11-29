#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
講座用語分析ツール - 工程1D

このスクリプトは、リサーチデータから重要な用語を抽出し、
学習フェーズへのマッピングと用語網羅性を分析します。

SEO_AI_ver6.5の工程3B（共起語抽出）を講座自動化に適応。
"""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from typing import Dict, List, Set


class CourseTerminologyAnalyzer:
    """講座用語分析クラス"""

    def __init__(self):
        self.analysis_date = datetime.now().isoformat()

        # 一般的なストップワード（除外する単語）
        self.stopwords = set([
            'これ', 'それ', 'あれ', 'この', 'その', 'あの',
            'こと', 'もの', 'ため', 'など', 'ここ', 'そこ', 'あそこ',
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'can', 'could', 'may', 'might', 'must', 'shall', 'should',
            'this', 'that', 'these', 'those', 'and', 'or', 'but', 'not'
        ])

    def extract_terminology_from_web(self, web_data: Dict) -> Dict:
        """
        Webリサーチデータから用語を抽出

        Args:
            web_data: Webリサーチデータ

        Returns:
            抽出された用語の辞書
        """
        if not web_data or not web_data.get('sources'):
            return {'status': 'no_data', 'terms': []}

        all_text = []
        for source in web_data.get('sources', []):
            content = source.get('content', '')
            title = source.get('title', '')
            all_text.append(title + ' ' + content)

        combined_text = ' '.join(all_text)

        # 用語抽出
        terms = self._extract_terms(combined_text)

        return {
            'status': 'extracted',
            'source_type': 'web',
            'terms': terms,
            'total_unique_terms': len(terms)
        }

    def extract_terminology_from_youtube(self, youtube_data: Dict) -> Dict:
        """
        YouTube文字起こしデータから用語を抽出

        Args:
            youtube_data: YouTube文字起こしデータ

        Returns:
            抽出された用語の辞書
        """
        if not youtube_data or not youtube_data.get('transcriptions'):
            return {'status': 'no_data', 'terms': []}

        all_text = []
        for transcript in youtube_data.get('transcriptions', []):
            text = transcript.get('text', '')
            all_text.append(text)

        combined_text = ' '.join(all_text)

        # 用語抽出
        terms = self._extract_terms(combined_text)

        return {
            'status': 'extracted',
            'source_type': 'youtube',
            'terms': terms,
            'total_unique_terms': len(terms)
        }

    def _extract_terms(self, text: str) -> List[Dict]:
        """
        テキストから重要な用語を抽出

        Args:
            text: 分析対象のテキスト

        Returns:
            用語のリスト
        """
        # 英数字を含む2文字以上の単語を抽出
        words = re.findall(r'\b[A-Za-z0-9ァ-ヴー]{2,}\b|[一-龯]{2,}', text)

        # 頻度カウント
        word_freq = Counter(words)

        # ストップワードを除外
        filtered_words = {
            word: freq for word, freq in word_freq.items()
            if word.lower() not in self.stopwords and freq >= 2
        }

        # 頻度順にソート
        sorted_terms = sorted(
            filtered_words.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # 上位50件を取得
        top_terms = []
        for term, frequency in sorted_terms[:50]:
            top_terms.append({
                'term': term,
                'frequency': frequency,
                'category': self._categorize_term(term),
                'learning_phase': None  # 後で割り当て
            })

        return top_terms

    def _categorize_term(self, term: str) -> str:
        """
        用語をカテゴリに分類

        Args:
            term: 用語

        Returns:
            カテゴリ名
        """
        # 技術用語の判定
        tech_patterns = [
            r'AI', r'API', r'ChatGPT', r'GPT', r'LLM', r'DX', r'IT',
            r'システム', r'プログラム', r'アルゴリズム', r'データ',
            r'ネットワーク', r'セキュリティ', r'クラウド'
        ]

        for pattern in tech_patterns:
            if re.search(pattern, term, re.IGNORECASE):
                return 'technical'

        # ビジネス用語の判定
        business_patterns = [
            r'業務', r'効率', r'生産性', r'コスト', r'売上', r'利益',
            r'マーケティング', r'営業', r'管理', r'戦略', r'経営'
        ]

        for pattern in business_patterns:
            if re.search(pattern, term, re.IGNORECASE):
                return 'business'

        # 教育・学習用語の判定
        learning_patterns = [
            r'学習', r'教育', r'研修', r'トレーニング', r'スキル',
            r'知識', r'理解', r'習得', r'実践'
        ]

        for pattern in learning_patterns:
            if re.search(pattern, term, re.IGNORECASE):
                return 'learning'

        return 'general'

    def map_to_learning_phases(self, terms: List[Dict], course_theme: str = None) -> List[Dict]:
        """
        用語を学習フェーズにマッピング

        Args:
            terms: 用語リスト
            course_theme: 講座テーマ（オプション）

        Returns:
            学習フェーズがマッピングされた用語リスト
        """
        # 学習フェーズ:
        # 1. 導入（Introduction）: 基本概念、定義、背景
        # 2. 理解（Understanding）: 仕組み、原理、詳細
        # 3. 実践（Application）: 使い方、活用法、事例

        for term_dict in terms:
            term = term_dict['term']
            category = term_dict['category']

            # カテゴリと頻度に基づいて学習フェーズを推定
            if category == 'learning' or '基本' in term or '概要' in term or '入門' in term:
                phase = 'introduction'
            elif '方法' in term or '使い方' in term or '活用' in term or '実践' in term or '事例' in term:
                phase = 'application'
            else:
                phase = 'understanding'

            term_dict['learning_phase'] = phase

        return terms

    def generate_terminology_report(
        self,
        web_terms: Dict,
        youtube_terms: Dict,
        course_theme: str = None
    ) -> Dict:
        """
        統合用語分析レポートを生成

        Args:
            web_terms: Web用語抽出結果
            youtube_terms: YouTube用語抽出結果
            course_theme: 講座テーマ（オプション）

        Returns:
            統合用語分析レポート
        """
        # 用語を統合
        all_terms = []

        if web_terms.get('status') == 'extracted':
            all_terms.extend(web_terms.get('terms', []))

        if youtube_terms.get('status') == 'extracted':
            all_terms.extend(youtube_terms.get('terms', []))

        # 重複を統合（同じ用語の頻度を合算）
        term_dict = {}
        for term_info in all_terms:
            term = term_info['term']
            if term in term_dict:
                term_dict[term]['frequency'] += term_info['frequency']
                term_dict[term]['sources'] = term_dict[term].get('sources', []) + [term_info.get('source_type', 'unknown')]
            else:
                term_dict[term] = term_info.copy()
                term_dict[term]['sources'] = [term_info.get('source_type', 'unknown')]

        # 統合用語リスト
        integrated_terms = list(term_dict.values())

        # 頻度順にソート
        integrated_terms.sort(key=lambda x: x['frequency'], reverse=True)

        # 上位30件に絞る
        top_terms = integrated_terms[:30]

        # 学習フェーズにマッピング
        top_terms = self.map_to_learning_phases(top_terms, course_theme)

        # レポート生成
        report = {
            'analysis_date': self.analysis_date,
            'course_theme': course_theme,
            'terminology_summary': {
                'total_unique_terms': len(integrated_terms),
                'top_terms_count': len(top_terms),
                'categories': self._count_categories(top_terms),
                'learning_phases': self._count_phases(top_terms)
            },
            'top_terms': top_terms,
            'recommendations': self._generate_terminology_recommendations(top_terms)
        }

        return report

    def _count_categories(self, terms: List[Dict]) -> Dict:
        """用語のカテゴリ別カウント"""
        categories = Counter(term['category'] for term in terms)
        return dict(categories)

    def _count_phases(self, terms: List[Dict]) -> Dict:
        """用語の学習フェーズ別カウント"""
        phases = Counter(term.get('learning_phase', 'unknown') for term in terms)
        return dict(phases)

    def _generate_terminology_recommendations(self, terms: List[Dict]) -> List[str]:
        """用語分析結果から推奨事項を生成"""
        recommendations = []

        # カテゴリ分布を確認
        categories = self._count_categories(terms)
        phases = self._count_phases(terms)

        # 技術用語が多い
        if categories.get('technical', 0) > len(terms) * 0.5:
            recommendations.append(
                "💡 技術用語が多く検出されました。初学者向けに用語解説を充実させることを推奨します。"
            )

        # ビジネス用語が多い
        if categories.get('business', 0) > len(terms) * 0.5:
            recommendations.append(
                "💡 ビジネス用語が多く検出されました。実務への応用事例を含めることを推奨します。"
            )

        # 学習フェーズのバランスを確認
        introduction_count = phases.get('introduction', 0)
        understanding_count = phases.get('understanding', 0)
        application_count = phases.get('application', 0)

        if introduction_count < len(terms) * 0.2:
            recommendations.append(
                "⚠️ 導入フェーズの用語が少ないです。基本概念の説明を充実させることを推奨します。"
            )

        if application_count < len(terms) * 0.2:
            recommendations.append(
                "⚠️ 実践フェーズの用語が少ないです。具体的な活用方法や事例を追加することを推奨します。"
            )

        if not recommendations:
            recommendations.append("✓ 用語のバランスは良好です。")

        # 重要用語の活用提案
        top_5_terms = [term['term'] for term in terms[:5]]
        recommendations.append(
            f"💡 重要用語トップ5: {', '.join(top_5_terms)}\n  これらの用語を講座の各セクションで適切に解説することを推奨します。"
        )

        return recommendations

    def save_report(self, report: Dict, output_path: str):
        """用語分析レポートを保存"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n💾 用語分析レポートを保存: {output_path}")
        except Exception as e:
            print(f"✗ レポート保存エラー: {e}", file=sys.stderr)

    def print_report_summary(self, report: Dict):
        """用語分析レポートのサマリーを表示"""
        print("\n" + "=" * 60)
        print("📖 講座用語分析レポート")
        print("=" * 60)

        summary = report.get('terminology_summary', {})

        print(f"\n📊 用語サマリー:")
        print(f"  - ユニーク用語数: {summary.get('total_unique_terms', 0)}個")
        print(f"  - トップ用語数: {summary.get('top_terms_count', 0)}個")

        # カテゴリ分布
        categories = summary.get('categories', {})
        if categories:
            print(f"\n🏷️ カテゴリ分布:")
            category_labels = {
                'technical': '技術用語',
                'business': 'ビジネス用語',
                'learning': '学習用語',
                'general': '一般用語'
            }
            for cat, count in categories.items():
                label = category_labels.get(cat, cat)
                print(f"  - {label}: {count}個")

        # 学習フェーズ分布
        phases = summary.get('learning_phases', {})
        if phases:
            print(f"\n📚 学習フェーズ分布:")
            phase_labels = {
                'introduction': '導入',
                'understanding': '理解',
                'application': '実践'
            }
            for phase, count in phases.items():
                label = phase_labels.get(phase, phase)
                print(f"  - {label}: {count}個")

        # トップ10用語
        top_terms = report.get('top_terms', [])[:10]
        if top_terms:
            print(f"\n🔝 頻出用語トップ10:")
            for i, term_info in enumerate(top_terms, 1):
                term = term_info['term']
                freq = term_info['frequency']
                category = term_info['category']
                phase = term_info.get('learning_phase', 'unknown')
                print(f"  {i:2d}. {term} (頻度: {freq}, カテゴリ: {category}, フェーズ: {phase})")

        # 推奨事項
        print(f"\n💡 推奨事項:")
        for rec in report.get('recommendations', []):
            print(f"  {rec}")

        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='講座用語分析ツール - リサーチデータから重要用語を抽出・分析'
    )

    parser.add_argument(
        '--web-research',
        help='Webリサーチデータ（JSON）のパス'
    )
    parser.add_argument(
        '--youtube-research',
        help='YouTube文字起こしデータ（JSON）のパス'
    )
    parser.add_argument(
        '--course-theme',
        help='講座テーマ（オプション）'
    )
    parser.add_argument(
        '--output',
        default='terminology_analysis_report.json',
        help='用語分析レポートの出力ファイル名（デフォルト: terminology_analysis_report.json）'
    )

    args = parser.parse_args()

    # 少なくとも1つの入力が必要
    if not args.web_research and not args.youtube_research:
        parser.error("--web-research または --youtube-research のいずれかを指定してください")

    print("=" * 60)
    print("📖 講座用語分析ツール - 工程1D")
    print("=" * 60)

    analyzer = CourseTerminologyAnalyzer()

    # Webリサーチデータから用語を抽出
    web_terms = {'status': 'skipped'}
    if args.web_research:
        print(f"\n📚 Webリサーチデータから用語を抽出中: {args.web_research}")
        try:
            with open(args.web_research, 'r', encoding='utf-8') as f:
                web_data = json.load(f)
            web_terms = analyzer.extract_terminology_from_web(web_data)
            print(f"  ✓ {web_terms.get('total_unique_terms', 0)}個のユニーク用語を抽出しました")
        except Exception as e:
            print(f"  ✗ エラー: {e}", file=sys.stderr)
            web_terms = {'status': 'error', 'message': str(e)}

    # YouTube文字起こしデータから用語を抽出
    youtube_terms = {'status': 'skipped'}
    if args.youtube_research:
        print(f"\n🎥 YouTube文字起こしデータから用語を抽出中: {args.youtube_research}")
        try:
            with open(args.youtube_research, 'r', encoding='utf-8') as f:
                youtube_data = json.load(f)
            youtube_terms = analyzer.extract_terminology_from_youtube(youtube_data)
            print(f"  ✓ {youtube_terms.get('total_unique_terms', 0)}個のユニーク用語を抽出しました")
        except Exception as e:
            print(f"  ✗ エラー: {e}", file=sys.stderr)
            youtube_terms = {'status': 'error', 'message': str(e)}

    # 統合用語分析レポートを生成
    report = analyzer.generate_terminology_report(
        web_terms,
        youtube_terms,
        args.course_theme
    )

    # レポートを保存
    analyzer.save_report(report, args.output)

    # サマリーを表示
    analyzer.print_report_summary(report)


if __name__ == '__main__':
    main()
