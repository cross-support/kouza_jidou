# 📋 講座自動化システム - プロジェクト情報

## 🎯 プロジェクト概要

**プロジェクト名**: 講座自動化ver1
**作成日**: 2024年
**最終更新**: 2025-11-30
**バージョン**: 1.0

---

## 📍 プロジェクト情報

### ローカル環境
```
パス: /Users/apple/Desktop/クロスリンク様/ラーニング講座/講座自動化ver1
```

### リモートリポジトリ
```
GitHub: https://github.com/cross-support/kouza_jidou
リポジトリタイプ: Public
```

### デプロイ環境
```
プラットフォーム: Streamlit Cloud
URL: https://kouza-jidou.streamlit.app (デプロイ後に確認)
自動デプロイ: 有効（GitHubプッシュで自動更新）
```

---

## 📁 ファイル構成

### メインファイル
- `app.py` - Streamlit Web UI（メインアプリケーション）
- `course_plan_parser.py` - 講座プロンプト生成
- `course_research.py` - Webリサーチ自動化
- `youtube_transcriber.py` - YouTube文字起こし
- `unified_research.py` - 統合リサーチツール
- `course_quality_validator.py` - 品質検証
- `course_terminology_analyzer.py` - 用語分析

### データファイル
- `自動R7.11 講座計画表.csv` - 講座構造データベース
- `requirements.txt` - Python依存パッケージ

### ドキュメント
- `README_Webアプリ.md` - Webアプリ使用方法
- `README_品質保証統合.md` - 品質保証機能説明
- `README_統合リサーチ.md` - リサーチツール説明
- `README_統合ワークフロー.md` - 全体ワークフロー
- `README_工程1A.md` - Webリサーチ詳細
- `PROJECT_INFO.md` - このファイル

### データディレクトリ
```
data/
├── projects/     # プロジェクト設定ファイル
├── outputs/      # リサーチ結果・レポート・プロンプト
```

---

## ✨ 実装済み機能一覧

### 基本機能（初期実装）
1. ✅ Webリサーチ自動化
2. ✅ YouTube文字起こし
3. ✅ 統合リサーチツール
4. ✅ 品質検証
5. ✅ 用語分析
6. ✅ Geminiプロンプト生成
7. ✅ Streamlit Web UI

### 追加機能（2025-11-30実装）
1. ✅ **複数ユニット対応**
   - カンマ区切りで複数ユニット指定（例: 1,2,3,4）
   - 全ユニット生成も可能（空欄時）

2. ✅ **全文取得**
   - Webページ: 10,000文字制限を撤廃 → 無制限
   - YouTube: 元から全文取得済み

3. ✅ **プロジェクトバックアップ/復元**
   - プロジェクト全体をJSONでダウンロード
   - バックアップから復元可能
   - 全データを含む（設定・リサーチ・レポート・プロンプト）

4. ✅ **プロンプト長さ確認**
   - リサーチ完了時にトークン数を自動推定
   - Gemini制限（2Mトークン）に対する使用率表示
   - 5段階の警告レベル（✅👍⚠️🔶❌）

5. ✅ **テンプレート機能**
   - 4つのプリセットテンプレート
   - 初心者向けAI講座
   - 中級者向けChatGPT活用講座
   - 経営層向けAI戦略講座
   - エンジニア向け技術講座

6. ✅ **自動保存機能**
   - URL追加・削除時に自動保存
   - データ損失防止
   - 「（自動保存済み）」の確認メッセージ

7. ✅ **URLプレビュー**
   - URL追加前にプレビュー確認
   - タイトルとスニペット表示
   - 不正URL検出

8. ✅ **統計ダッシュボード**
   - 全プロジェクトの統計表示
   - 総プロジェクト数・URL数・リサーチ完了数
   - プロジェクト一覧

---

## 🛠️ 技術スタック

### フロントエンド
- **Streamlit** (>=1.28.0) - Web UI フレームワーク

### バックエンド
- **Python 3** - メイン言語
- **Pandas** (>=2.0.0) - データ処理
- **Requests** (>=2.31.0) - HTTP通信
- **BeautifulSoup4** (>=4.12.0) - HTMLパース
- **youtube-transcript-api** (>=0.6.0) - YouTube文字起こし
- **duckduckgo-search** (>=4.0.0) - Web検索（現在は未使用）

### デプロイ
- **Streamlit Cloud** - ホスティング
- **GitHub** - バージョン管理・自動デプロイ

---

## 🔄 ワークフロー

```
ステップ1: URL入力
  ↓
ステップ2: リサーチ実行
  ├─ Webリサーチ (course_research.py)
  └─ YouTube文字起こし (youtube_transcriber.py)
  ↓
ステップ3: 品質・用語分析
  ├─ 品質検証 (course_quality_validator.py)
  └─ 用語分析 (course_terminology_analyzer.py)
  ↓
ステップ4: 講座設定
  └─ テンプレート適用可能
  ↓
ステップ5: プロンプト生成
  └─ Gemini用プロンプト生成 (course_plan_parser.py)
  ↓
Gemini AI で講座コンテンツ生成
```

---

## 📊 システムの完成度

| カテゴリ | 完成度 |
|---------|--------|
| 基本機能 | 100% ✅ |
| 効率化機能 | 100% ✅ |
| 品質管理 | 100% ✅ |
| データ保護 | 100% ✅ |
| 可視化 | 100% ✅ |
| **総合** | **95%以上** 🌟 |

---

## 🚀 デプロイ手順

### 初回デプロイ
1. GitHubにコードをプッシュ
2. Streamlit Cloud (https://share.streamlit.io/) にアクセス
3. GitHubアカウントでサインイン
4. リポジトリ選択: `cross-support/kouza_jidou`
5. メインファイル: `app.py`
6. デプロイ実行

### 更新デプロイ
```bash
git add .
git commit -m "更新内容"
git push
```
→ Streamlit Cloudが自動的に再デプロイ（2-3分）

---

## 🔧 ローカル実行方法

### 起動
```bash
cd "/Users/apple/Desktop/クロスリンク様/ラーニング講座/講座自動化ver1"
streamlit run app.py
```

または

```bash
python3 -m streamlit run app.py
```

### アクセス
```
http://localhost:8501
```

---

## 📝 次回のセッションで継続する方法

### 継続開発を始めるには

次回のセッション開始時に、以下のいずれかを伝えてください：

**パターン1（シンプル）**:
```
「講座自動化ver1」の開発を続けたいです
```

**パターン2（詳細）**:
```
前回開発した講座自動化システム
(/Users/apple/Desktop/クロスリンク様/ラーニング講座/講座自動化ver1)
に新機能を追加したいです。
```

**パターン3（具体的なタスク）**:
```
講座自動化システムに○○機能を追加したいです。
前回のコードを確認してから実装してください。
```

---

## 💡 今後の拡張可能性

### 未実装の機能候補
- ⬜ バッチ処理機能（複数プロジェクトの一括処理）
- ⬜ Gemini API直接統合
- ⬜ 生成された講座の管理機能
- ⬜ プロジェクト共有機能
- ⬜ スケジュール実行
- ⬜ より高度なNLP分析
- ⬜ データベース統合（永続化）

---

## 🔐 認証情報

### GitHub Personal Access Token
```
トークン: [ローカル環境に保存済み]
用途: GitHubへのプッシュ
取得方法: https://github.com/settings/tokens
```

⚠️ **注意**: トークンは機密情報です。gitリポジトリにコミットしないでください。

---

## 📞 トラブルシューティング

### よくある問題と解決方法

#### 問題1: Streamlitが起動しない
```bash
# 解決方法
pip3 install streamlit
# または
python3 -m pip install streamlit
```

#### 問題2: 依存パッケージが不足
```bash
# 解決方法
pip3 install -r requirements.txt
```

#### 問題3: データが消えた
```
原因: Streamlit Cloudではファイルが一時的
解決: バックアップ機能を使用して定期的にダウンロード
```

#### 問題4: GitHubプッシュエラー
```bash
# 解決方法: リモートURLを更新
git remote set-url origin https://ghp_TOKEN@github.com/cross-support/kouza_jidou.git
```

---

## 📅 開発履歴

### 2025-11-30
- ✅ 複数ユニット対応実装
- ✅ 全文取得対応（Web無制限化）
- ✅ プロジェクトバックアップ/復元機能実装
- ✅ プロンプト長さ確認機能実装
- ✅ テンプレート機能実装
- ✅ 自動保存機能実装
- ✅ URLプレビュー機能実装
- ✅ 統計ダッシュボード実装
- ✅ GitHubにデプロイ
- ✅ Streamlit Cloud設定完了

---

## 🎯 プロジェクトの目的

このシステムは、**e-ラーニング講座の自動生成**を目的としています：

1. WebとYouTubeから情報を自動収集
2. 収集した情報の品質を検証
3. 重要な用語を分析
4. Gemini AIで講座コンテンツを生成するためのプロンプトを作成
5. 効率的な講座制作ワークフローを実現

---

**作成者**: Claude Code
**最終更新**: 2025-11-30
**バージョン**: 1.0
**ステータス**: 本番運用可能 ✅
