# 統合リサーチツール - 工程1A + 1B

## 📋 概要

`unified_research.py` は、Webリサーチ（工程1A）とYouTube文字起こし（工程1B）を
**1つのコマンドで実行**できる統合ツールです。

従来は2つのスクリプトを別々に実行する必要がありましたが、このツールを使用することで、
講座リサーチを効率的に実施できます。

## 🎯 機能

- ✅ WebリサーチとYouTube文字起こしを一括実行
- ✅ 両方のリサーチ結果をJSON形式で保存
- ✅ 統合サマリーレポートの自動生成
- ✅ 次のステップ（講座生成）のコマンド例を自動表示
- ✅ 柔軟な実行オプション（Web のみ、YouTube のみも可能）

## 🔄 従来の方法 vs 統合ツール

### 従来の方法（2ステップ）

```bash
# ステップ1: Webリサーチ
python3 course_research.py \
  --url-list web_urls.txt \
  --output web_research.json

# ステップ2: YouTube文字起こし
python3 youtube_transcriber.py \
  --url-list youtube_urls.txt \
  --output youtube_transcripts.json
```

### 統合ツール（1ステップ）⭐

```bash
# 1つのコマンドで両方実行
python3 unified_research.py \
  --web-urls web_urls.txt \
  --youtube-urls youtube_urls.txt
```

## 📖 使用方法

### 基本的な使い方

```bash
python3 unified_research.py \
  --web-urls <WebのURLリストファイル> \
  --youtube-urls <YouTubeのURLリストファイル>
```

### 出力ファイル名をカスタマイズ

```bash
python3 unified_research.py \
  --web-urls web_urls.txt \
  --youtube-urls youtube_urls.txt \
  --web-output my_web_research.json \
  --youtube-output my_youtube_transcripts.json \
  --summary-output my_summary.json
```

### YouTube字幕の言語を指定

```bash
python3 unified_research.py \
  --web-urls web_urls.txt \
  --youtube-urls youtube_urls.txt \
  --languages ja en ko
```

### Webリサーチのみ実行

```bash
python3 unified_research.py \
  --web-urls web_urls.txt
```

### YouTube文字起こしのみ実行

```bash
python3 unified_research.py \
  --youtube-urls youtube_urls.txt
```

## 🎛️ コマンドラインオプション

| オプション | 必須 | デフォルト値 | 説明 |
|-----------|------|-------------|------|
| `--web-urls` | - | なし | WebのURLリストファイル（省略可） |
| `--youtube-urls` | - | なし | YouTubeのURLリストファイル（省略可） |
| `--web-output` | - | `web_research.json` | Webリサーチの出力ファイル名 |
| `--youtube-output` | - | `youtube_transcripts.json` | YouTube文字起こしの出力ファイル名 |
| `--summary-output` | - | `research_summary.json` | 統合サマリーの出力ファイル名 |
| `--languages` | - | `ja en` | YouTube字幕の言語コード（複数指定可） |

**注意**: `--web-urls` と `--youtube-urls` のいずれかは必須です。両方省略するとエラーになります。

## 📁 入力ファイル形式

### WebのURLリスト（例: web_urls.txt）

```
# ChatGPTに関する情報源
https://ja.wikipedia.org/wiki/ChatGPT
https://www.itmedia.co.jp/
https://qiita.com/

# コメント行は # で始める
# 空行は無視されます
```

### YouTubeのURLリスト（例: youtube_urls.txt）

```
# ChatGPT解説動画
https://www.youtube.com/watch?v=VIDEO_ID_1
https://youtu.be/VIDEO_ID_2

# 動画IDのみでもOK
VIDEO_ID_3
```

## 📊 出力ファイル

### 1. Webリサーチ結果（web_research.json）

```json
{
  "research_date": "2025-11-30T08:02:42.373114",
  "source_type": "url_list",
  "total_sources": 4,
  "sources": [
    {
      "url": "https://ja.wikipedia.org/wiki/ChatGPT",
      "title": "ChatGPT - Wikipedia",
      "content": "...",
      "character_count": 10003,
      "extraction_date": "2025-11-30T08:02:42.123456"
    }
  ],
  "summary": {
    "total_characters": 22238,
    "average_characters": 5559
  }
}
```

### 2. YouTube文字起こし結果（youtube_transcripts.json）

```json
{
  "transcription_date": "2025-11-30T08:02:43.397852",
  "source_type": "youtube",
  "total_videos": 1,
  "successful_transcriptions": 1,
  "transcriptions": [
    {
      "video_id": "8pTEmbeENF4",
      "source_url": "https://www.youtube.com/watch?v=8pTEmbeENF4",
      "language": "en",
      "text": "...",
      "word_count": 30041,
      "total_duration": 1968.1,
      "segments": [...]
    }
  ],
  "summary": {
    "total_words": 30041,
    "total_duration": 1968.1,
    "languages_used": ["en"]
  }
}
```

### 3. 統合サマリー（research_summary.json）★

```json
{
  "unified_research_date": "2025-11-30T08:02:43.422618",
  "web_research": {
    "status": "success",
    "sources": 4,
    "characters": 22238
  },
  "youtube_research": {
    "status": "success",
    "videos": 1,
    "characters": 30041,
    "duration_minutes": 32.8
  },
  "total": {
    "total_sources": 5,
    "total_characters": 52279
  }
}
```

## 🖥️ 実行例とコンソール出力

### コマンド実行

```bash
python3 unified_research.py \
  --web-urls sample_urls_chatgpt.txt \
  --youtube-urls sample_youtube_urls.txt
```

### コンソール出力

```
============================================================
🚀 統合リサーチツール - 工程1A + 1B
============================================================
実行日時: 2025-11-30 08:02:37

============================================================
📚 工程1A: Webリサーチを開始
============================================================
... [Webリサーチの進捗] ...

============================================================
🎥 工程1B: YouTube文字起こしを開始
============================================================
... [YouTube文字起こしの進捗] ...

============================================================
📊 統合リサーチ完了サマリー
============================================================

📚 Webリサーチ: ✓ SUCCESS
  - 情報源: 4件
  - 文字数: 22,238文字

🎥 YouTube文字起こし: ✓ SUCCESS
  - 動画数: 1件
  - 文字数: 30,041文字
  - 総再生時間: 32.8分

📈 合計:
  - 総情報源: 5件
  - 総文字数: 52,279文字
============================================================

💾 統合サマリーを保存: research_summary.json

============================================================
📝 次のステップ:
============================================================
以下のコマンドで講座生成プロンプトを作成できます:

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
  > gemini_prompt.txt

============================================================
```

## 🎯 完全なワークフロー例

### ステップ1: URLリストを準備

**web_urls.txt**
```
https://ja.wikipedia.org/wiki/ChatGPT
https://www.itmedia.co.jp/
https://qiita.com/
```

**youtube_urls.txt**
```
https://www.youtube.com/watch?v=8pTEmbeENF4
https://www.youtube.com/watch?v=ANOTHER_VIDEO_ID
```

### ステップ2: 統合リサーチを実行

```bash
python3 unified_research.py \
  --web-urls web_urls.txt \
  --youtube-urls youtube_urls.txt \
  --web-output chatgpt_web.json \
  --youtube-output chatgpt_youtube.json
```

### ステップ3: 講座生成プロンプトを作成

```bash
python3 course_plan_parser.py \
  --csv "自動R7.11 講座計画表.csv" \
  --course "ChatGPT業務活用の基本" \
  --format canvas-script \
  --learner_profile "ChatGPTを業務で使いたいビジネスパーソン" \
  --target_behavior "ChatGPTを適切に活用して業務効率を向上できる" \
  --duration "30分" \
  --tone "親しみやすく、実践的なトーン" \
  --web-research "chatgpt_web.json" \
  --youtube-research "chatgpt_youtube.json" \
  > chatgpt_gemini_prompt.txt
```

### ステップ4: Gemini AIで実行

`chatgpt_gemini_prompt.txt` の内容をGemini AIにコピー＆ペーストして実行。

## ⚙️ 内部動作

### 処理フロー

```
1. コマンドライン引数の解析
   ↓
2. Webリサーチ実行（--web-urls が指定されている場合）
   - course_research.py をサブプロセスとして実行
   - 結果JSONファイルを読み込み
   ↓
3. YouTube文字起こし実行（--youtube-urls が指定されている場合）
   - youtube_transcriber.py をサブプロセスとして実行
   - 結果JSONファイルを読み込み
   ↓
4. 統合サマリーの生成
   - 両方の結果を統合
   - 統計情報を計算
   ↓
5. 結果の出力
   - コンソールにサマリー表示
   - research_summary.json に保存
   - 次のステップのコマンド例を表示
```

### エラーハンドリング

- いずれかのリサーチが失敗しても、他方が成功すれば継続
- サブプロセスのエラーは標準エラー出力に表示
- 終了コード:
  - `0`: 全て成功
  - `1`: 両方失敗
  - `2`: 一部失敗

## 🔧 トラブルシューティング

### エラー: course_research.py が見つかりません

**原因**: unified_research.py と同じディレクトリに course_research.py が存在しない

**解決策**:
```bash
# 正しいディレクトリで実行しているか確認
ls course_research.py
ls youtube_transcriber.py
ls unified_research.py
```

### エラー: --web-urls または --youtube-urls のいずれかを指定してください

**原因**: 両方のオプションが省略されている

**解決策**: 少なくとも1つのオプションを指定
```bash
# OK: Web のみ
python3 unified_research.py --web-urls web_urls.txt

# OK: YouTube のみ
python3 unified_research.py --youtube-urls youtube_urls.txt

# OK: 両方
python3 unified_research.py --web-urls web_urls.txt --youtube-urls youtube_urls.txt

# NG: 両方省略
python3 unified_research.py  # エラー
```

### 一部のリサーチが失敗する

**現象**: Webリサーチは成功したが、YouTube文字起こしが失敗

**確認事項**:
1. YouTubeのURLリストファイルが存在するか
2. 動画に字幕が存在するか
3. 言語コードが適切か（`--languages ja en` など）

**対処法**:
```bash
# 失敗したリサーチのみ再実行
python3 unified_research.py \
  --youtube-urls youtube_urls.txt \
  --youtube-output youtube_transcripts.json
```

## 💡 ヒントとベストプラクティス

### 推奨URL数

- **Web記事**: 3〜5件（バランスが良い）
- **YouTube動画**: 1〜3件（文字起こしテキストが長いため）

多すぎるとGemini AIのトークン制限に達する可能性があります。

### 言語の優先順位

```bash
# 日本語を最優先、次に英語、韓国語
python3 unified_research.py \
  --youtube-urls urls.txt \
  --languages ja en ko
```

左側の言語が優先されます。

### 段階的なリサーチ

最初は少ないURL数でテストすることを推奨：

```bash
# テスト: 各1件のみ
python3 unified_research.py \
  --web-urls test_web.txt \    # 1件のURL
  --youtube-urls test_yt.txt   # 1件のURL
```

問題なければ、本番用のURLリストで実行。

## 📈 パフォーマンス

### 実行時間の目安

- **Webリサーチ**: 1件あたり 2〜5秒
- **YouTube文字起こし**: 1件あたり 3〜10秒

例: Web 4件 + YouTube 2件 = 約30〜60秒

### 並列処理について

現在の実装では、Webリサーチ → YouTube文字起こしの順に**逐次実行**されます。
将来的に並列実行に対応する可能性があります。

## 📝 関連ドキュメント

- **README_統合ワークフロー.md**: 全体のワークフロー説明
- **README_工程1A.md**: Webリサーチの詳細
- **講座生成_指示書.md**: システム全体の使用方法

## 🔄 更新履歴

- **v1.0** (2025-11-30): 初版リリース
  - Webリサーチと YouTube文字起こしの統合
  - 統合サマリーレポート機能
  - 次のステップ案内機能

---

**作成日**: 2025-11-30
**バージョン**: 1.0
**スクリプト**: `unified_research.py`
