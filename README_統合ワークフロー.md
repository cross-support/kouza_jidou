# 講座自動化システム - 統合ワークフロー

## 📋 概要

このシステムは、Webリサーチ、YouTube動画文字起こし、講座コンテンツ生成を統合したワークフローです。
事前リサーチデータを活用することで、より正確で実践的な講座コンテンツを生成できます。

## 🔄 ワークフロー全体像

### 方法A: 統合リサーチツールを使用（推奨）⭐

```
工程1（統合）: Webリサーチ + YouTube文字起こし (unified_research.py)
    ↓
工程2: 講座生成 (course_plan_parser.py)
    ↓
Gemini AIによる講座コンテンツ生成
```

### 方法B: 個別実行

```
工程1A: Webリサーチ (course_research.py)
    ↓
工程1B: YouTube文字起こし (youtube_transcriber.py)
    ↓
工程2: 講座生成 (course_plan_parser.py)
    ↓
Gemini AIによる講座コンテンツ生成
```

---

## 工程1: 統合リサーチ（推奨）⭐

### 目的
WebリサーチとYouTube文字起こしを**1つのコマンドで実行**し、効率的にリサーチデータを収集します。

### 使用方法

```bash
python3 unified_research.py \
  --web-urls sample_urls_chatgpt.txt \
  --youtube-urls sample_youtube_urls.txt
```

### 入力
- WebのURLリストファイル（省略可）
- YouTubeのURLリストファイル（省略可）
- 字幕言語コード（オプション）

### 出力
- `web_research.json` - Webリサーチデータ
- `youtube_transcripts.json` - YouTube文字起こしデータ
- `research_summary.json` - 統合サマリー ★

### メリット
- ✅ 1つのコマンドで両方のリサーチを実行
- ✅ 統合サマリーで全体像を把握
- ✅ 次のステップのコマンド例を自動表示
- ✅ エラーハンドリングが統一されている

### 詳細ドキュメント
→ `README_統合リサーチ.md` を参照

---

## 工程1A: Webリサーチ（情報収集）【個別実行】

### 目的
講座テーマに関連するWeb記事から情報を収集し、JSON形式で保存します。

### 使用方法

```bash
python3 course_research.py \
  --url-list sample_urls_chatgpt.txt \
  --output chatgpt_web_research.json
```

### 入力
- URLリストファイル（1行に1URL、`#`でコメント可）

### 出力
- JSON形式のリサーチデータ
  - 各ソースのURL、タイトル、本文
  - 総文字数、収集日時などのメタデータ

### 詳細ドキュメント
→ `README_工程1A.md` を参照

---

## 工程1B: YouTube文字起こし【個別実行】

### 目的
YouTube動画から字幕データを取得し、文字起こしテキストとして保存します。

### 使用方法

```bash
python3 youtube_transcriber.py \
  --url-list sample_youtube_urls.txt \
  --output chatgpt_youtube_transcripts.json \
  --languages ja en
```

### 入力
- YouTube URLリストファイル（1行に1URL）
- 言語コード（デフォルト: ja, en）

### 出力
- JSON形式の文字起こしデータ
  - 各動画の文字起こしテキスト
  - タイムスタンプ付きセグメント
  - 総文字数、動画時間などのメタデータ

### サポートされるURL形式
```
https://www.youtube.com/watch?v=VIDEO_ID
https://youtu.be/VIDEO_ID
https://www.youtube.com/embed/VIDEO_ID
VIDEO_ID（11文字の英数字）
```

---

## 工程2: 講座コンテンツ生成（統合版）

### 目的
CSV講座計画表とリサーチデータを統合し、Gemini AI用のプロンプトを生成します。

### 基本使用方法（リサーチデータなし）

```bash
python3 course_plan_parser.py \
  --csv "自動R7.11 講座計画表.csv" \
  --course "ChatGPT業務活用の基本" \
  --format canvas-script \
  --learner_profile "ChatGPTを業務で使いたいビジネスパーソン" \
  --target_behavior "ChatGPTを適切に活用して業務効率を向上できる" \
  --duration "30分" \
  --tone "親しみやすく、実践的なトーン"
```

### 統合使用方法（リサーチデータあり）★推奨★

```bash
python3 course_plan_parser.py \
  --csv "自動R7.11 講座計画表.csv" \
  --course "ChatGPT業務活用の基本" \
  --format canvas-script \
  --learner_profile "ChatGPTを業務で使いたいビジネスパーソン" \
  --target_behavior "ChatGPTを適切に活用して業務効率を向上できる" \
  --duration "30分" \
  --tone "親しみやすく、実践的なトーン" \
  --web-research "chatgpt_web_research.json" \
  --youtube-research "chatgpt_youtube_transcripts.json"
```

### パラメータ説明

| パラメータ | 必須 | 説明 |
|-----------|------|------|
| `--csv` | ✓ | 講座計画表CSVファイルのパス |
| `--course` | ✓ | 生成する講座名（CSV内の講座名と一致） |
| `--format` | ✓ | 出力フォーマット（現在は`canvas-script`のみ） |
| `--learner_profile` | ✓ | 受講者像 |
| `--target_behavior` | ✓ | 到達目標（ゴール行動） |
| `--duration` | ✓ | 想定時間 |
| `--tone` | ✓ | トーン＆マナー |
| `--unit` | - | 特定のユニットのみ生成（省略可） |
| `--web-research` | - | Webリサーチデータ（JSON）のパス |
| `--youtube-research` | - | YouTube文字起こしデータ（JSON）のパス |

### 出力

標準出力に、Gemini AI用のプロンプトが出力されます。
プロンプトには以下が含まれます：

1. **講座の全体仕様**（テーマ、受講者像、目標など）
2. **講座構成**（ユニット、スライドのリスト）
3. **📊 事前リサーチデータ**（Webリサーチ + YouTube文字起こし）← 統合版の追加機能
4. **タスク指示**（Canvas用スライド設計図 + ナレーション台本の生成指示）

---

## 💡 完全な使用例

### ステップ1: URLリストを作成

**web_urls.txt**
```
# ChatGPTに関する情報源
https://ja.wikipedia.org/wiki/ChatGPT
https://www.itmedia.co.jp/
https://qiita.com/
```

**youtube_urls.txt**
```
# ChatGPT解説動画
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
```

### ステップ2: リサーチ実行

#### 方法A: 統合リサーチツールを使用（推奨）⭐

```bash
# 1つのコマンドで両方実行
python3 unified_research.py \
  --web-urls web_urls.txt \
  --youtube-urls youtube_urls.txt \
  --web-output chatgpt_web_research.json \
  --youtube-output chatgpt_youtube_transcripts.json
```

#### 方法B: 個別に実行

```bash
# Webリサーチ
python3 course_research.py \
  --url-list web_urls.txt \
  --output chatgpt_web_research.json

# YouTube文字起こし
python3 youtube_transcriber.py \
  --url-list youtube_urls.txt \
  --output chatgpt_youtube_transcripts.json
```

### ステップ3: 講座生成プロンプトを生成

```bash
python3 course_plan_parser.py \
  --csv "自動R7.11 講座計画表.csv" \
  --course "ChatGPT業務活用の基本" \
  --format canvas-script \
  --learner_profile "ChatGPTを業務で使いたいビジネスパーソン" \
  --target_behavior "ChatGPTを適切に活用して業務効率を向上できる" \
  --duration "30分" \
  --tone "親しみやすく、実践的なトーン" \
  --web-research "chatgpt_web_research.json" \
  --youtube-research "chatgpt_youtube_transcripts.json" \
  > gemini_prompt.txt
```

### ステップ4: Gemini AIで実行

生成された `gemini_prompt.txt` をGemini AIにコピー＆ペーストして実行します。

---

## 🎯 リサーチデータ統合のメリット

### 従来版（リサーチなし）
- 一般的な知識のみでコンテンツを生成
- 最新情報や具体例が不足する可能性

### 統合版（リサーチあり）★
- **最新情報**: Web記事から最新のトレンドや事例を取得
- **実践的内容**: YouTube動画から実際の使用例や説明を学習
- **信頼性向上**: 複数の情報源を参照することで正確性が向上
- **具体例豊富**: リアルなケーススタディや事例を含めることが可能

---

## 📁 ファイル構成

```
講座自動化ver1/
├── unified_research.py         # 工程1: 統合リサーチツール ⭐推奨⭐
├── course_research.py          # 工程1A: Webリサーチツール（個別実行用）
├── youtube_transcriber.py      # 工程1B: YouTube文字起こしツール（個別実行用）
├── course_plan_parser.py       # 工程2: 講座生成（統合版）
├── 自動R7.11 講座計画表.csv    # 講座構造データベース
├── README_統合リサーチ.md      # 統合リサーチツールの詳細
├── README_工程1A.md            # 工程1Aの詳細ドキュメント
├── README_統合ワークフロー.md  # このファイル（全体ワークフロー）
└── サンプルファイル/
    ├── sample_urls_chatgpt.txt
    └── sample_youtube_urls.txt
```

---

## 🔧 トラブルシューティング

### リサーチデータが読み込まれない
- ファイルパスが正しいか確認してください
- JSONファイルが正しい形式か確認してください
- エラーメッセージは標準エラー出力（stderr）に表示されます

### YouTube字幕が取得できない
- 動画に字幕が存在するか確認してください
- 言語コードを変更してみてください（`--languages en ja ko`など）
- 一部の動画は字幕が無効化されている場合があります

### 講座名が見つからない
- CSV内の講座名と完全一致する名前を指定してください
- エラーメッセージに類似する講座名が表示されます

---

## 📊 出力例

### リサーチデータの統計情報（標準エラー出力）

```
📚 Webリサーチデータを読み込み中: chatgpt_web_research.json
  ✓ 4件の情報源を読み込みました
🎥 YouTube文字起こしデータを読み込み中: chatgpt_youtube_transcripts.json
  ✓ 2件の動画を読み込みました
```

### プロンプト内のリサーチデータセクション

```markdown
# 📊 事前リサーチデータ（講座作成の参考情報）
以下のリサーチデータは、講座内容をより正確で実践的なものにするための参考資料です。

### 📚 Web リサーチデータ
- 収集日: 2025-11-30T07:48:25.027190
- 情報源数: 4件
- 総文字数: 22,302文字

**情報源1: ChatGPT - Wikipedia**
- URL: https://ja.wikipedia.org/wiki/ChatGPT
- 文字数: 5,800文字
- 内容抜粋: ChatGPT（チャットジーピーティー）は...

### 🎥 YouTube 文字起こしデータ
- 文字起こし日: 2025-11-30T07:54:40.904264
- 動画数: 2件
- 総文字数: 45,123文字
- 総再生時間: 48.5分

**動画1: VIDEO_ID**
- URL: https://www.youtube.com/watch?v=VIDEO_ID
- 言語: ja
- 文字数: 20,500文字
- 動画時間: 25.3分
- 内容抜粋: 今日はChatGPTの基本的な使い方について...
```

---

## 🚀 次のステップ

### 現在完了している機能
- ✅ 工程1A: Webリサーチ
- ✅ 工程1B: YouTube文字起こし
- ✅ 工程2: リサーチデータ統合

### 今後の拡張予定
- ⬜ 工程1C: ファクトチェック機能
- ⬜ ブログ自動化プロンプトの統合
- ⬜ 共起語抽出（工程3B）の統合
- ⬜ 統合リサーチスクリプト（1Aと1Bを1つに）

---

## 📝 補足

### リサーチデータの推奨件数
- **Web記事**: 3〜5件（多すぎるとプロンプトが長くなります）
- **YouTube動画**: 1〜3件（文字起こしテキストが長いため）

### プロンプトサイズ
- リサーチデータなし: 約3,000文字
- リサーチデータあり: 10,000〜50,000文字（リサーチ内容による）

Gemini AIのトークン制限に注意してください。

---

**作成日**: 2025-11-30
**バージョン**: 1.0
**統合機能追加**: course_plan_parser.py（工程1A/1B統合版）
