# 品質保証統合システム - SEO_AI_ver6.5ロジックの適応

## 📋 概要

このドキュメントでは、SEO_AI_ver6.5のブログ自動化ロジック（ファクトチェック・用語抽出）を
講座自動化システムに統合した、品質保証機能について説明します。

## 🎯 統合された機能

### 元のSEO_AI_ver6.5機能 → 講座自動化への適応

| SEO_AI_ver6.5 | 講座自動化 | 目的 |
|--------------|----------|------|
| **工程8**: ファクトチェック | **工程1C**: 品質検証 | リサーチデータの品質評価 |
| **工程3B**: 共起語抽出 | **工程1D**: 用語分析 | 重要用語の抽出とマッピング |

## 🔄 拡張ワークフロー

```
工程1: リサーチ (unified_research.py)
  ↓
工程1C: 品質検証 (course_quality_validator.py) ← 新規追加
  ↓
工程1D: 用語分析 (course_terminology_analyzer.py) ← 新規追加
  ↓
工程2: 講座生成 (course_plan_parser.py) ← 品質保証統合版
  ↓
Gemini AIによる高品質な講座コンテンツ生成
```

---

## 工程1C: 講座コンテンツ品質検証

### 目的
リサーチデータの品質を検証し、講座コンテンツ生成の品質保証を行います。

### 検証項目

#### Webリサーチデータ
- ✅ URLの有効性
- ✅ コンテンツの存在確認
- ✅ 数値データの検出
- ✅ 情報源の信頼性評価（ドメイン判定）

#### YouTube文字起こしデータ
- ✅ 文字起こしテキストの品質
- ✅ 動画時間と文字数の妥当性
- ✅ 言語の確認
- ✅ セグメント数の確認

### 使用方法

```bash
python3 course_quality_validator.py \
  --web-research web_research.json \
  --youtube-research youtube_transcripts.json \
  --output quality_report.json
```

### 出力

#### 品質評価レベル
- `excellent` (優秀): 7点以上
- `good` (良好): 5-6点
- `acceptable` (許容範囲): 3-4点
- `needs_improvement` (改善必要): 2点以下

#### 評価基準（各項目0-2点）
1. **情報源の数**: 5件以上 = 2点、3-4件 = 1点
2. **データポイント**: 20件以上 = 2点、10-19件 = 1点
3. **信頼性の高い情報源**: 3件以上 = 2点、1-2件 = 1点
4. **コンテンツボリューム**: 10,000語以上 = 2点、5,000-9,999語 = 1点

### 出力例

```json
{
  "validation_date": "2025-11-30T08:05:00.000000",
  "overall_quality": "good",
  "integrated_summary": {
    "total_information_sources": 5,
    "total_data_points": 9,
    "credible_sources": 3,
    "total_content_volume": {
      "web_characters": 22238,
      "youtube_words": 30041
    }
  },
  "quality_recommendations": [
    "✓ 良好な品質のリサーチデータです。",
    "💡 9件の数値データが検出されました。これらを講座の具体例として活用できます。"
  ]
}
```

---

## 工程1D: 講座用語分析

### 目的
リサーチデータから重要な用語を抽出し、学習フェーズへマッピングすることで、
用語網羅性を確保します。

### 分析項目

#### 用語抽出
- 頻度2回以上の2文字以上の単語を抽出
- ストップワード（一般的な機能語）を除外
- 上位50件を抽出

#### 用語分類
- **technical** (技術用語): AI, システム、プログラムなど
- **business** (ビジネス用語): 業務、効率、生産性など
- **learning** (学習用語): 学習、教育、研修など
- **general** (一般用語): その他

#### 学習フェーズマッピング
- **introduction** (導入): 基本概念、定義、背景
- **understanding** (理解): 仕組み、原理、詳細
- **application** (実践): 使い方、活用法、事例

### 使用方法

```bash
python3 course_terminology_analyzer.py \
  --web-research web_research.json \
  --youtube-research youtube_transcripts.json \
  --course-theme "ChatGPT業務活用" \
  --output terminology_report.json
```

### 出力例

```json
{
  "analysis_date": "2025-11-30T08:05:00.000000",
  "course_theme": "ChatGPT業務活用",
  "terminology_summary": {
    "total_unique_terms": 50,
    "top_terms_count": 30,
    "categories": {
      "technical": 15,
      "business": 10,
      "learning": 3,
      "general": 2
    },
    "learning_phases": {
      "introduction": 8,
      "understanding": 15,
      "application": 7
    }
  },
  "top_terms": [
    {
      "term": "ChatGPT",
      "frequency": 45,
      "category": "technical",
      "learning_phase": "introduction"
    },
    ...
  ],
  "recommendations": [
    "💡 技術用語が多く検出されました。初学者向けに用語解説を充実させることを推奨します。"
  ]
}
```

---

## 工程2: 品質保証統合版講座生成

### 拡張された機能

従来の `course_plan_parser.py` に以下の機能を追加しました：

1. **品質検証レポートの読み込み** (`--quality-report`)
2. **用語分析レポートの読み込み** (`--terminology-report`)
3. **品質保証データのプロンプト統合**

### 使用方法

#### 基本（品質保証なし）

```bash
python3 course_plan_parser.py \
  --csv "自動R7.11 講座計画表.csv" \
  --course "講座名" \
  --format canvas-script \
  --learner_profile "受講者像" \
  --target_behavior "到達目標" \
  --duration "30分" \
  --tone "トーン" \
  --web-research "web_research.json" \
  --youtube-research "youtube_transcripts.json"
```

#### 品質保証統合版（推奨）⭐

```bash
python3 course_plan_parser.py \
  --csv "自動R7.11 講座計画表.csv" \
  --course "講座名" \
  --format canvas-script \
  --learner_profile "受講者像" \
  --target_behavior "到達目標" \
  --duration "30分" \
  --tone "トーン" \
  --web-research "web_research.json" \
  --youtube-research "youtube_transcripts.json" \
  --quality-report "quality_report.json" \
  --terminology-report "terminology_report.json"
```

### Geminiプロンプトへの統合内容

品質保証データは、以下の形式でGeminiプロンプトに組み込まれます：

```markdown
### 🔍 品質保証データ（講座作成の指針）

**品質評価**: 良好
- データポイント数: 9件
- 信頼性の高い情報源: 3件

**品質に関する注意点**:
- ✓ 良好な品質のリサーチデータです。
- ⚠️ 数値データが少ない。統計データを含む情報源を追加することを推奨します。

**重要用語分析**:
- 検出された重要用語数: 50個
- カテゴリ分布: technical: 15個, business: 10個
- 学習フェーズ分布: 導入: 8個, 理解: 15個, 実践: 7個

**必ず解説すべき重要用語トップ10**:
ChatGPT, AI, プロンプト, 業務効率, 自動化, 生産性, システム, データ, 活用方法, 事例

→ これらの用語は講座内で明確に定義し、適切に解説してください。

**用語に関する推奨事項**:
- 💡 技術用語が多く検出されました。初学者向けに用語解説を充実させることを推奨します。
- ⚠️ 実践フェーズの用語が少ないです。具体的な活用方法や事例を追加することを推奨します。
```

---

## 💡 完全な使用例

### ステップ1: リサーチ実行

```bash
python3 unified_research.py \
  --web-urls web_urls.txt \
  --youtube-urls youtube_urls.txt \
  --web-output web_research.json \
  --youtube-output youtube_transcripts.json
```

### ステップ2: 品質検証

```bash
python3 course_quality_validator.py \
  --web-research web_research.json \
  --youtube-research youtube_transcripts.json \
  --output quality_report.json
```

### ステップ3: 用語分析

```bash
python3 course_terminology_analyzer.py \
  --web-research web_research.json \
  --youtube-research youtube_transcripts.json \
  --course-theme "ChatGPT業務活用" \
  --output terminology_report.json
```

### ステップ4: 講座生成（品質保証統合版）

```bash
python3 course_plan_parser.py \
  --csv "自動R7.11 講座計画表.csv" \
  --course "ChatGPT業務活用の基本" \
  --format canvas-script \
  --learner_profile "ChatGPTを業務で使いたいビジネスパーソン" \
  --target_behavior "ChatGPTを適切に活用して業務効率を向上できる" \
  --duration "30分" \
  --tone "親しみやすく、実践的なトーン" \
  --web-research "web_research.json" \
  --youtube-research "youtube_transcripts.json" \
  --quality-report "quality_report.json" \
  --terminology-report "terminology_report.json" \
  > gemini_prompt.txt
```

### ステップ5: Gemini AIで実行

`gemini_prompt.txt` の内容をGemini AIにコピー＆ペーストして実行。

---

## 📊 品質保証のメリット

### 従来版（品質保証なし）
- リサーチデータをそのままGeminiに渡す
- データの品質や網羅性は不明
- 重要用語の抜け漏れの可能性

### 品質保証統合版（推奨）⭐
- ✅ **データ品質の可視化**: リサーチデータの品質を定量評価
- ✅ **用語網羅性の確保**: 重要用語を明示的にリストアップ
- ✅ **学習フェーズの最適化**: 用語を導入/理解/実践にマッピング
- ✅ **Geminiへの明示的指示**: 品質に関する注意点を具体的に伝達
- ✅ **教育的価値の向上**: 信頼性の高い情報源の活用を促進

---

## 🔍 SEO_AI_ver6.5からの適応内容

### 工程8（ファクトチェック）→ 工程1C（品質検証）

#### 適応した要素
- ✅ データアンカーの検証 → 数値データの検出
- ✅ 引用元の実在確認 → 情報源の信頼性評価
- ✅ URLの有効性確認 → そのまま適用
- ✅ 問題点の特定 → 推奨事項の生成

#### 講座用にカスタマイズした点
- ブログのSEO評価 → 教育コンテンツの品質評価
- 引用元の厳密な検証 → ドメイン基準の信頼性評価
- FAQの生成 → 用語解説の推奨

### 工程3B（共起語抽出）→ 工程1D（用語分析）

#### 適応した要素
- ✅ 共起語の抽出 → 重要用語の抽出
- ✅ 3フェーズマッピング → 学習フェーズマッピング
  - 不安→理解→行動 → 導入→理解→実践
- ✅ キーワード分類 → 用語カテゴリ分類

#### 講座用にカスタマイズした点
- SEOキーワード最適化 → 教育用語の網羅性確保
- 検索意図の分析 → 学習フェーズの分析
- CTA用キーワード → 実践フェーズの用語

---

## 📁 ファイル構成（更新版）

```
講座自動化ver1/
├── unified_research.py              # 工程1: 統合リサーチ
├── course_quality_validator.py      # 工程1C: 品質検証 ⭐新規⭐
├── course_terminology_analyzer.py   # 工程1D: 用語分析 ⭐新規⭐
├── course_plan_parser.py            # 工程2: 講座生成（品質保証統合版）⭐更新⭐
├── 自動R7.11 講座計画表.csv        # 講座構造データベース
├── README_品質保証統合.md           # このファイル
├── README_統合ワークフロー.md       # 全体ワークフロー（更新予定）
└── SEO_AI_ver6.5/                   # 参照元（ブログ自動化システム）
    ├── 工程8_ファクトチェック/
    └── 工程3B_共起語・関連キーワード抽出/
```

---

## 🔧 トラブルシューティング

### 品質評価が低い場合

**品質評価: 改善必要**

→ 以下を確認：
- 情報源の数は十分か（最低3件推奨）
- YouTube動画の文字起こしは取得できているか
- 信頼性の高い情報源（.gov、.edu、Wikipedia等）を含んでいるか

### 用語が適切に抽出されない場合

**検出された重要用語数: 0個**

→ 以下を確認：
- リサーチデータに十分なテキストがあるか
- 日本語または英語のテキストがあるか
- ストップワードに重要な用語が含まれていないか

### 学習フェーズの偏りが大きい場合

**学習フェーズ分布: 理解: 90%, 導入: 5%, 実践: 5%**

→ 推奨事項：
- 導入フェーズが少ない → 基本概念を説明する情報源を追加
- 実践フェーズが少ない → 活用事例や具体的な方法を説明する情報源を追加

---

## 🎯 今後の拡張可能性

### 現在実装済み
- ✅ 基本的な品質検証
- ✅ 用語抽出と分類
- ✅ 学習フェーズマッピング
- ✅ Geminiプロンプトへの統合

### 今後の拡張候補
- ⬜ リアルタイムのURLアクセス検証
- ⬜ より高度な自然言語処理（NLP）による用語抽出
- ⬜ 自動的な用語定義の生成
- ⬜ コンテンツの難易度分析
- ⬜ 学習目標との整合性チェック

---

**作成日**: 2025-11-30
**バージョン**: 1.0
**SEO_AI_ver6.5適応**: 工程8（ファクトチェック）+ 工程3B（共起語抽出）
