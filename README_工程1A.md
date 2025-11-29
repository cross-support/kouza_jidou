# 工程1A: Google検索による情報収集

## 📖 概要

`course_research.py` は、講座のテーマやキーワードからWeb上の関連情報を自動収集するツールです。

ブログ自動化システムの工程5（一次情報追加）を参考に、講座作成向けにカスタマイズしています。

## 🎯 機能

- **Google検索**: 指定キーワードで自動検索
- **コンテンツ抽出**: 検索結果のURLから本文を自動抽出
- **データ整理**: JSON形式で収集データを保存
- **複数キーワード対応**: 複数のキーワードで一括検索可能

## 📦 必要なライブラリ

初回のみ、以下のコマンドでライブラリをインストールしてください:

```bash
pip3 install requests beautifulsoup4
```

## 🚀 使い方

### 基本的な使い方

```bash
python3 course_research.py \
  --keywords "ChatGPT 業務活用" \
  --num-results 10 \
  --output research_chatgpt.json
```

### パラメータ説明

| パラメータ | 必須 | 説明 | デフォルト |
|-----------|------|------|-----------|
| `--keywords` | ✓ | 検索キーワード（複数指定可） | なし |
| `--num-results` | | 各キーワードで取得する検索結果数 | 10 |
| `--output` | | 出力JSONファイル名 | course_research_output.json |

### 使用例

#### 例1: 単一キーワードで検索

```bash
python3 course_research.py \
  --keywords "新入社員研修" \
  --num-results 15
```

#### 例2: 複数キーワードで検索

```bash
python3 course_research.py \
  --keywords "ChatGPT 業務活用" "AI ビジネス活用" "生成AI 事例" \
  --num-results 10 \
  --output chatgpt_research.json
```

#### 例3: 講座CSVと組み合わせて使用

```bash
# まず情報収集
python3 course_research.py \
  --keywords "ChatGPT 業務活用の基本" \
  --output research_output.json

# 次に講座生成（既存のスクリプト）
python3 course_plan_parser.py \
  --csv "自動R7.11 講座計画表.csv" \
  --course "ChatGPT業務活用の基本" \
  --format canvas-script \
  --learner_profile "社内の全従業員" \
  --target_behavior "ChatGPTで業務効率化できる" \
  --duration "1時間" \
  --tone "丁寧でフレンドリー"
```

## 📊 出力形式

出力されるJSONファイルの構造:

```json
{
  "research_date": "2025-11-30T00:00:00",
  "keywords": ["ChatGPT 業務活用"],
  "total_sources": 10,
  "sources": [
    {
      "title": "記事タイトル",
      "url": "https://example.com/article",
      "text": "抽出された本文...",
      "word_count": 5000,
      "search_keyword": "ChatGPT 業務活用",
      "search_snippet": "検索結果のスニペット"
    }
  ],
  "summary": {
    "total_words": 50000,
    "unique_urls": 10
  }
}
```

## ⚠️ 注意事項

1. **レート制限**: Google検索に負荷をかけないよう、リクエスト間に1秒の待機時間を設けています
2. **文字数制限**: 各ページから最大10,000文字まで抽出します
3. **エラー処理**: アクセスできないURLはスキップされます
4. **検索精度**: Google検索の仕様変更により、取得できる結果数が変動する場合があります

## 🔧 トラブルシューティング

### エラー: Required library not found

ライブラリがインストールされていません。以下を実行してください:

```bash
pip3 install requests beautifulsoup4
```

### 検索結果が0件

- インターネット接続を確認してください
- キーワードを変更してみてください
- `--num-results` の値を調整してください

### コンテンツ取得エラーが多い

一部のサイトはアクセス制限がある場合があります。これは正常な動作です。

## 🎓 次のステップ

工程1Aで収集したデータは、以下の用途に活用できます:

1. **講座内容の裏付け**: 収集した情報をもとに講座の信頼性を高める
2. **最新トレンドの把握**: 最新の情報をキャッチアップ
3. **事例の収集**: 実際の活用事例を講座に組み込む

次の工程:
- **工程1B**: YouTube動画の文字起こし（準備中）
- **工程1C**: ファクトチェック（準備中）
