#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
講座コンテンツ品質検証ツール - 工程1C

このスクリプトは、リサーチデータの品質を検証し、
講座コンテンツ生成のための品質保証レポートを作成します。

SEO_AI_ver6.5の工程8（ファクトチェック）を講座自動化に適応。
"""

import argparse
import json
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse


class CourseQualityValidator:
    """講座コンテンツ品質検証クラス"""

    def __init__(self):
        self.validation_date = datetime.now().isoformat()

    def validate_web_research(self, web_data: Dict) -> Dict:
        """
        Webリサーチデータを検証

        Args:
            web_data: Webリサーチデータ

        Returns:
            検証結果の辞書
        """
        if not web_data or not web_data.get('sources'):
            return {
                'status': 'no_data',
                'message': 'Webリサーチデータがありません'
            }

        sources = web_data.get('sources', [])
        validations = []

        for i, source in enumerate(sources, 1):
            validation = {
                'source_number': i,
                'url': source.get('url', ''),
                'title': source.get('title', ''),
                'checks': {}
            }

            # URLの有効性チェック
            url = source.get('url', '')
            validation['checks']['url_valid'] = self._validate_url(url)

            # コンテンツの存在確認
            content = source.get('content', '')
            char_count = source.get('character_count', 0)
            validation['checks']['has_content'] = len(content) > 100 or char_count > 100
            validation['checks']['content_length'] = len(content)

            # 数値データの検出
            numbers_found = re.findall(r'\d+(?:\.\d+)?%|\d+(?:,\d{3})*(?:\.\d+)?', content)
            validation['checks']['data_points_found'] = len(numbers_found)
            validation['checks']['sample_data'] = numbers_found[:5] if numbers_found else []

            # 信頼性評価（ドメイン判定）
            validation['checks']['source_credibility'] = self._evaluate_credibility(url)

            validations.append(validation)

        # サマリー
        summary = {
            'total_sources': len(sources),
            'valid_urls': sum(1 for v in validations if v['checks']['url_valid']),
            'sources_with_content': sum(1 for v in validations if v['checks']['has_content']),
            'total_data_points': sum(v['checks']['data_points_found'] for v in validations),
            'credible_sources': sum(1 for v in validations if v['checks']['source_credibility'] in ['high', 'medium'])
        }

        return {
            'status': 'validated',
            'summary': summary,
            'validations': validations,
            'recommendations': self._generate_web_recommendations(summary, validations)
        }

    def validate_youtube_research(self, youtube_data: Dict) -> Dict:
        """
        YouTube文字起こしデータを検証

        Args:
            youtube_data: YouTube文字起こしデータ

        Returns:
            検証結果の辞書
        """
        if not youtube_data or not youtube_data.get('transcriptions'):
            return {
                'status': 'no_data',
                'message': 'YouTube文字起こしデータがありません'
            }

        transcriptions = youtube_data.get('transcriptions', [])
        validations = []

        for i, transcript in enumerate(transcriptions, 1):
            validation = {
                'video_number': i,
                'video_id': transcript.get('video_id', ''),
                'url': transcript.get('source_url', ''),
                'checks': {}
            }

            # 文字起こしテキストの品質チェック
            text = transcript.get('text', '')
            word_count = transcript.get('word_count', 0)

            validation['checks']['has_transcript'] = len(text) > 100 or word_count > 100
            validation['checks']['word_count'] = word_count
            validation['checks']['duration_minutes'] = transcript.get('total_duration', 0) / 60

            # 言語確認
            validation['checks']['language'] = transcript.get('language', 'unknown')

            # 数値データの検出
            numbers_found = re.findall(r'\d+(?:\.\d+)?%|\d+(?:,\d{3})*(?:\.\d+)?', text)
            validation['checks']['data_points_found'] = len(numbers_found)
            validation['checks']['sample_data'] = numbers_found[:5] if numbers_found else []

            # セグメント数
            segments = transcript.get('segments', [])
            validation['checks']['segment_count'] = len(segments)

            validations.append(validation)

        # サマリー
        summary = {
            'total_videos': len(transcriptions),
            'videos_with_transcripts': sum(1 for v in validations if v['checks']['has_transcript']),
            'total_words': sum(v['checks']['word_count'] for v in validations),
            'total_duration_minutes': sum(v['checks']['duration_minutes'] for v in validations),
            'total_data_points': sum(v['checks']['data_points_found'] for v in validations),
            'languages': list(set(v['checks']['language'] for v in validations))
        }

        return {
            'status': 'validated',
            'summary': summary,
            'validations': validations,
            'recommendations': self._generate_youtube_recommendations(summary, validations)
        }

    def generate_quality_report(self, web_validation: Dict, youtube_validation: Dict) -> Dict:
        """
        統合品質レポートを生成

        Args:
            web_validation: Web検証結果
            youtube_validation: YouTube検証結果

        Returns:
            統合品質レポート
        """
        report = {
            'validation_date': self.validation_date,
            'overall_quality': 'unknown',
            'web_research': web_validation,
            'youtube_research': youtube_validation,
            'integrated_summary': {},
            'quality_recommendations': []
        }

        # 統合サマリー
        web_summary = web_validation.get('summary', {})
        youtube_summary = youtube_validation.get('summary', {})

        report['integrated_summary'] = {
            'total_information_sources': (
                web_summary.get('total_sources', 0) +
                youtube_summary.get('total_videos', 0)
            ),
            'total_data_points': (
                web_summary.get('total_data_points', 0) +
                youtube_summary.get('total_data_points', 0)
            ),
            'credible_sources': web_summary.get('credible_sources', 0),
            'total_content_volume': {
                'web_characters': sum(
                    v['checks']['content_length']
                    for v in web_validation.get('validations', [])
                ),
                'youtube_words': youtube_summary.get('total_words', 0)
            }
        }

        # 総合品質評価
        report['overall_quality'] = self._evaluate_overall_quality(report['integrated_summary'])

        # 統合推奨事項
        report['quality_recommendations'] = self._generate_integrated_recommendations(
            web_validation,
            youtube_validation,
            report['integrated_summary']
        )

        return report

    def _validate_url(self, url: str) -> bool:
        """URLの基本的な有効性を確認"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _evaluate_credibility(self, url: str) -> str:
        """情報源の信頼性を評価"""
        if not url:
            return 'unknown'

        # 高信頼性ドメイン
        high_credibility = [
            'wikipedia.org', '.gov', '.edu', '.go.jp', '.ac.jp',
            'scholar.google', 'researchgate.net', 'arxiv.org'
        ]

        # 中程度の信頼性
        medium_credibility = [
            'itmedia.co.jp', 'nikkei.com', 'diamond.jp', 'forbes.com',
            'techcrunch.com', 'qiita.com', 'zenn.dev', 'github.com'
        ]

        url_lower = url.lower()

        for domain in high_credibility:
            if domain in url_lower:
                return 'high'

        for domain in medium_credibility:
            if domain in url_lower:
                return 'medium'

        return 'low'

    def _generate_web_recommendations(self, summary: Dict, validations: List[Dict]) -> List[str]:
        """Web検証結果から推奨事項を生成"""
        recommendations = []

        # コンテンツが不足している情報源
        if summary['sources_with_content'] < summary['total_sources']:
            missing = summary['total_sources'] - summary['sources_with_content']
            recommendations.append(
                f"⚠️ {missing}件の情報源でコンテンツが不足しています。別のURLを検討してください。"
            )

        # データポイントが少ない
        if summary['total_data_points'] < 10:
            recommendations.append(
                f"⚠️ 数値データが少ない（{summary['total_data_points']}件）です。統計データを含む情報源を追加することを推奨します。"
            )

        # 信頼性の低い情報源が多い
        credible_ratio = summary['credible_sources'] / summary['total_sources'] if summary['total_sources'] > 0 else 0
        if credible_ratio < 0.5:
            recommendations.append(
                f"⚠️ 信頼性の高い情報源が少ない（{summary['credible_sources']}/{summary['total_sources']}件）です。"
                "公的機関や学術機関の情報源を追加することを推奨します。"
            )

        if not recommendations:
            recommendations.append("✓ Webリサーチデータは良好な品質です。")

        return recommendations

    def _generate_youtube_recommendations(self, summary: Dict, validations: List[Dict]) -> List[str]:
        """YouTube検証結果から推奨事項を生成"""
        recommendations = []

        # 文字起こしが不足
        if summary['videos_with_transcripts'] < summary['total_videos']:
            missing = summary['total_videos'] - summary['videos_with_transcripts']
            recommendations.append(
                f"⚠️ {missing}件の動画で文字起こしが不足しています。字幕のある動画を選択してください。"
            )

        # 総文字数が少ない
        if summary['total_words'] < 5000:
            recommendations.append(
                f"⚠️ 総文字数が少ない（{summary['total_words']:,}語）です。より長い動画または追加の動画を検討してください。"
            )

        # 動画時間が短い
        if summary['total_duration_minutes'] < 10:
            recommendations.append(
                f"⚠️ 総動画時間が短い（{summary['total_duration_minutes']:.1f}分）です。より詳細な解説動画を追加することを推奨します。"
            )

        if not recommendations:
            recommendations.append("✓ YouTube文字起こしデータは良好な品質です。")

        return recommendations

    def _evaluate_overall_quality(self, integrated_summary: Dict) -> str:
        """統合サマリーから総合品質を評価"""
        score = 0

        # 情報源の数
        total_sources = integrated_summary.get('total_information_sources', 0)
        if total_sources >= 5:
            score += 2
        elif total_sources >= 3:
            score += 1

        # データポイントの数
        total_data_points = integrated_summary.get('total_data_points', 0)
        if total_data_points >= 20:
            score += 2
        elif total_data_points >= 10:
            score += 1

        # 信頼性の高い情報源
        credible_sources = integrated_summary.get('credible_sources', 0)
        if credible_sources >= 3:
            score += 2
        elif credible_sources >= 1:
            score += 1

        # コンテンツボリューム
        youtube_words = integrated_summary.get('total_content_volume', {}).get('youtube_words', 0)
        if youtube_words >= 10000:
            score += 2
        elif youtube_words >= 5000:
            score += 1

        # 評価
        if score >= 7:
            return 'excellent'
        elif score >= 5:
            return 'good'
        elif score >= 3:
            return 'acceptable'
        else:
            return 'needs_improvement'

    def _generate_integrated_recommendations(
        self,
        web_validation: Dict,
        youtube_validation: Dict,
        integrated_summary: Dict
    ) -> List[str]:
        """統合推奨事項を生成"""
        recommendations = []

        quality = self._evaluate_overall_quality(integrated_summary)

        if quality == 'excellent':
            recommendations.append("✓ 優れた品質のリサーチデータです。講座コンテンツ生成に十分な情報があります。")
        elif quality == 'good':
            recommendations.append("✓ 良好な品質のリサーチデータです。")
        elif quality == 'acceptable':
            recommendations.append("⚠️ 許容範囲内の品質ですが、以下の改善を推奨します：")
        else:
            recommendations.append("❌ 品質改善が必要です。以下の対策を実施してください：")

        # 個別の推奨事項を追加
        if web_validation.get('status') == 'validated':
            recommendations.extend(web_validation.get('recommendations', []))

        if youtube_validation.get('status') == 'validated':
            recommendations.extend(youtube_validation.get('recommendations', []))

        # 講座生成への影響を評価
        total_data_points = integrated_summary.get('total_data_points', 0)
        if total_data_points > 0:
            recommendations.append(
                f"💡 {total_data_points}件の数値データが検出されました。これらを講座の具体例として活用できます。"
            )

        return recommendations

    def save_report(self, report: Dict, output_path: str):
        """品質レポートを保存"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n💾 品質検証レポートを保存: {output_path}")
        except Exception as e:
            print(f"✗ レポート保存エラー: {e}", file=sys.stderr)

    def print_report_summary(self, report: Dict):
        """品質レポートのサマリーを表示"""
        print("\n" + "=" * 60)
        print("📊 講座コンテンツ品質検証レポート")
        print("=" * 60)

        # 総合品質
        quality = report.get('overall_quality', 'unknown')
        quality_icons = {
            'excellent': '🌟',
            'good': '✓',
            'acceptable': '⚠️',
            'needs_improvement': '❌',
            'unknown': '?'
        }
        quality_labels = {
            'excellent': '優秀',
            'good': '良好',
            'acceptable': '許容範囲',
            'needs_improvement': '改善必要',
            'unknown': '不明'
        }

        icon = quality_icons.get(quality, '?')
        label = quality_labels.get(quality, '不明')
        print(f"\n{icon} 総合品質評価: {label}")

        # 統合サマリー
        summary = report.get('integrated_summary', {})
        print(f"\n📈 統合サマリー:")
        print(f"  - 総情報源数: {summary.get('total_information_sources', 0)}件")
        print(f"  - データポイント数: {summary.get('total_data_points', 0)}件")
        print(f"  - 信頼性の高い情報源: {summary.get('credible_sources', 0)}件")

        volume = summary.get('total_content_volume', {})
        print(f"  - コンテンツ量:")
        print(f"    • Web: {volume.get('web_characters', 0):,}文字")
        print(f"    • YouTube: {volume.get('youtube_words', 0):,}語")

        # 推奨事項
        print(f"\n💡 推奨事項:")
        for rec in report.get('quality_recommendations', []):
            print(f"  {rec}")

        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='講座コンテンツ品質検証ツール - リサーチデータの品質をチェック'
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
        '--output',
        default='quality_validation_report.json',
        help='品質検証レポートの出力ファイル名（デフォルト: quality_validation_report.json）'
    )

    args = parser.parse_args()

    # 少なくとも1つの入力が必要
    if not args.web_research and not args.youtube_research:
        parser.error("--web-research または --youtube-research のいずれかを指定してください")

    print("=" * 60)
    print("📋 講座コンテンツ品質検証ツール - 工程1C")
    print("=" * 60)

    validator = CourseQualityValidator()

    # Webリサーチデータを検証
    web_validation = {'status': 'skipped'}
    if args.web_research:
        print(f"\n📚 Webリサーチデータを検証中: {args.web_research}")
        try:
            with open(args.web_research, 'r', encoding='utf-8') as f:
                web_data = json.load(f)
            web_validation = validator.validate_web_research(web_data)
            print(f"  ✓ {web_validation.get('summary', {}).get('total_sources', 0)}件の情報源を検証しました")
        except Exception as e:
            print(f"  ✗ エラー: {e}", file=sys.stderr)
            web_validation = {'status': 'error', 'message': str(e)}

    # YouTube文字起こしデータを検証
    youtube_validation = {'status': 'skipped'}
    if args.youtube_research:
        print(f"\n🎥 YouTube文字起こしデータを検証中: {args.youtube_research}")
        try:
            with open(args.youtube_research, 'r', encoding='utf-8') as f:
                youtube_data = json.load(f)
            youtube_validation = validator.validate_youtube_research(youtube_data)
            print(f"  ✓ {youtube_validation.get('summary', {}).get('total_videos', 0)}件の動画を検証しました")
        except Exception as e:
            print(f"  ✗ エラー: {e}", file=sys.stderr)
            youtube_validation = {'status': 'error', 'message': str(e)}

    # 統合品質レポートを生成
    report = validator.generate_quality_report(web_validation, youtube_validation)

    # レポートを保存
    validator.save_report(report, args.output)

    # サマリーを表示
    validator.print_report_summary(report)


if __name__ == '__main__':
    main()
