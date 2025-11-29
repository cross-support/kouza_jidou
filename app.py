#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
講座自動化システム - Streamlit管理画面
カラフルで使いやすいWebインターフェース
"""

import streamlit as st
import pandas as pd
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import time

# ページ設定
st.set_page_config(
    page_title="講座自動化システム",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .step-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .info-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# データディレクトリの作成
DATA_DIR = Path(__file__).parent / "data"
PROJECTS_DIR = DATA_DIR / "projects"
OUTPUTS_DIR = DATA_DIR / "outputs"

for dir_path in [DATA_DIR, PROJECTS_DIR, OUTPUTS_DIR]:
    dir_path.mkdir(exist_ok=True)

# セッション状態の初期化
if 'current_project' not in st.session_state:
    st.session_state.current_project = None
if 'web_urls' not in st.session_state:
    st.session_state.web_urls = []
if 'youtube_urls' not in st.session_state:
    st.session_state.youtube_urls = []
if 'research_completed' not in st.session_state:
    st.session_state.research_completed = False
if 'quality_completed' not in st.session_state:
    st.session_state.quality_completed = False
if 'terminology_completed' not in st.session_state:
    st.session_state.terminology_completed = False
if 'prompt_generated' not in st.session_state:
    st.session_state.prompt_generated = False

# ヘッダー
st.markdown('<h1 class="main-header">📚 講座自動化システム</h1>', unsafe_allow_html=True)
st.markdown("---")

# サイドバー - プロジェクト管理
with st.sidebar:
    st.markdown("## 🎯 プロジェクト管理")

    # 新規プロジェクト
    with st.expander("➕ 新規プロジェクト作成", expanded=False):
        new_project_name = st.text_input("プロジェクト名", key="new_project")
        if st.button("作成", key="create_project"):
            if new_project_name:
                project_path = PROJECTS_DIR / f"{new_project_name}.json"
                if not project_path.exists():
                    project_data = {
                        "name": new_project_name,
                        "created_at": datetime.now().isoformat(),
                        "web_urls": [],
                        "youtube_urls": [],
                        "course_config": {}
                    }
                    with open(project_path, 'w', encoding='utf-8') as f:
                        json.dump(project_data, f, ensure_ascii=False, indent=2)
                    st.success(f"✅ プロジェクト '{new_project_name}' を作成しました！")
                    st.session_state.current_project = new_project_name
                    st.rerun()
                else:
                    st.error("同名のプロジェクトが既に存在します")

    # 既存プロジェクト読み込み
    projects = [p.stem for p in PROJECTS_DIR.glob("*.json")]
    if projects:
        st.markdown("### 📁 既存プロジェクト")
        selected_project = st.selectbox(
            "プロジェクトを選択",
            [""] + projects,
            key="select_project"
        )
        if selected_project and selected_project != st.session_state.current_project:
            st.session_state.current_project = selected_project
            # プロジェクトデータを読み込み
            with open(PROJECTS_DIR / f"{selected_project}.json", 'r', encoding='utf-8') as f:
                project_data = json.load(f)
                st.session_state.web_urls = project_data.get('web_urls', [])
                st.session_state.youtube_urls = project_data.get('youtube_urls', [])
            st.success(f"✅ プロジェクト '{selected_project}' を読み込みました")
            st.rerun()

    # 現在のプロジェクト表示
    if st.session_state.current_project:
        st.markdown("---")
        st.markdown(f"### 📌 現在のプロジェクト")
        st.info(f"**{st.session_state.current_project}**")

        # プロジェクト保存ボタン
        if st.button("💾 プロジェクト保存", key="save_project"):
            project_data = {
                "name": st.session_state.current_project,
                "updated_at": datetime.now().isoformat(),
                "web_urls": st.session_state.web_urls,
                "youtube_urls": st.session_state.youtube_urls,
            }
            with open(PROJECTS_DIR / f"{st.session_state.current_project}.json", 'w', encoding='utf-8') as f:
                json.dump(project_data, f, ensure_ascii=False, indent=2)
            st.success("✅ 保存しました！")

# メインコンテンツ
if not st.session_state.current_project:
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("### 👈 まず左のサイドバーから新規プロジェクトを作成するか、既存プロジェクトを選択してください")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # タブで各ステップを分ける
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔗 ステップ1: URL入力",
        "🔍 ステップ2: リサーチ実行",
        "📊 ステップ3: 品質・用語分析",
        "⚙️ ステップ4: 講座設定",
        "📝 ステップ5: プロンプト生成"
    ])

    # ========== タブ1: URL入力 ==========
    with tab1:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("### 🌐 Web記事のURL")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([4, 1])
        with col1:
            new_web_url = st.text_input(
                "WebのURLを入力",
                placeholder="https://example.com/article",
                key="new_web_url"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ 追加", key="add_web_url"):
                if new_web_url and new_web_url not in st.session_state.web_urls:
                    st.session_state.web_urls.append(new_web_url)
                    st.success("追加しました！")
                    st.rerun()

        # 登録済みURL一覧
        if st.session_state.web_urls:
            st.markdown("#### 📋 登録済みURL")
            for i, url in enumerate(st.session_state.web_urls):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.text(f"{i+1}. {url}")
                with col2:
                    if st.button("🗑️", key=f"delete_web_{i}"):
                        st.session_state.web_urls.pop(i)
                        st.rerun()
        else:
            st.info("URLを追加してください（3〜5件推奨）")

        st.markdown("---")

        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("### 🎥 YouTube動画のURL")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([4, 1])
        with col1:
            new_youtube_url = st.text_input(
                "YouTubeのURLを入力",
                placeholder="https://www.youtube.com/watch?v=...",
                key="new_youtube_url"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ 追加", key="add_youtube_url"):
                if new_youtube_url and new_youtube_url not in st.session_state.youtube_urls:
                    st.session_state.youtube_urls.append(new_youtube_url)
                    st.success("追加しました！")
                    st.rerun()

        # 登録済みURL一覧
        if st.session_state.youtube_urls:
            st.markdown("#### 📋 登録済みURL")
            for i, url in enumerate(st.session_state.youtube_urls):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.text(f"{i+1}. {url}")
                with col2:
                    if st.button("🗑️", key=f"delete_youtube_{i}"):
                        st.session_state.youtube_urls.pop(i)
                        st.rerun()
        else:
            st.info("URLを追加してください（1〜3件推奨）")

        # サマリー
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Web記事", f"{len(st.session_state.web_urls)}件")
        with col2:
            st.metric("YouTube動画", f"{len(st.session_state.youtube_urls)}件")
        with col3:
            total = len(st.session_state.web_urls) + len(st.session_state.youtube_urls)
            st.metric("合計", f"{total}件")

    # ========== タブ2: リサーチ実行 ==========
    with tab2:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("### 🚀 リサーチ実行")
        st.markdown('</div>', unsafe_allow_html=True)

        if not st.session_state.web_urls and not st.session_state.youtube_urls:
            st.warning("⚠️ まずステップ1でURLを追加してください")
        else:
            st.info(f"📊 Web記事: {len(st.session_state.web_urls)}件 | YouTube動画: {len(st.session_state.youtube_urls)}件")

            if st.button("🚀 リサーチ開始", key="start_research", type="primary"):
                # URLリストファイルを作成
                project_name = st.session_state.current_project
                web_urls_file = OUTPUTS_DIR / f"{project_name}_web_urls.txt"
                youtube_urls_file = OUTPUTS_DIR / f"{project_name}_youtube_urls.txt"

                if st.session_state.web_urls:
                    with open(web_urls_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(st.session_state.web_urls))

                if st.session_state.youtube_urls:
                    with open(youtube_urls_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(st.session_state.youtube_urls))

                # プログレスバー
                progress_bar = st.progress(0)
                status_text = st.empty()

                # unified_research.py を実行
                status_text.text("🔄 統合リサーチを実行中...")
                progress_bar.progress(10)

                cmd = [
                    sys.executable,
                    "unified_research.py",
                ]

                if st.session_state.web_urls:
                    cmd.extend(["--web-urls", str(web_urls_file)])
                if st.session_state.youtube_urls:
                    cmd.extend(["--youtube-urls", str(youtube_urls_file)])

                cmd.extend([
                    "--web-output", str(OUTPUTS_DIR / f"{project_name}_web.json"),
                    "--youtube-output", str(OUTPUTS_DIR / f"{project_name}_youtube.json"),
                    "--summary-output", str(OUTPUTS_DIR / f"{project_name}_summary.json")
                ])

                try:
                    progress_bar.progress(30)
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd=Path(__file__).parent
                    )

                    progress_bar.progress(70)

                    if result.returncode == 0:
                        progress_bar.progress(100)
                        st.session_state.research_completed = True
                        status_text.empty()
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.markdown("### ✅ リサーチ完了！")
                        st.markdown('</div>', unsafe_allow_html=True)

                        # サマリーを表示
                        summary_file = OUTPUTS_DIR / f"{project_name}_summary.json"
                        if summary_file.exists():
                            with open(summary_file, 'r', encoding='utf-8') as f:
                                summary = json.load(f)

                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric(
                                    "総情報源",
                                    summary.get('total', {}).get('total_sources', 0)
                                )
                            with col2:
                                st.metric(
                                    "総文字数",
                                    f"{summary.get('total', {}).get('total_characters', 0):,}"
                                )
                            with col3:
                                web_sources = summary.get('web_research', {}).get('sources', 0)
                                yt_videos = summary.get('youtube_research', {}).get('videos', 0)
                                st.metric("成功率", f"{web_sources + yt_videos}/{len(st.session_state.web_urls) + len(st.session_state.youtube_urls)}")

                        # 出力を表示
                        with st.expander("📄 実行ログを見る"):
                            st.code(result.stdout)
                    else:
                        progress_bar.progress(0)
                        st.error(f"❌ エラーが発生しました")
                        st.code(result.stderr)

                except Exception as e:
                    progress_bar.progress(0)
                    st.error(f"❌ エラー: {str(e)}")

            # リサーチ完了済みの場合
            if st.session_state.research_completed:
                st.markdown("---")
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown("### ✅ リサーチ完了済み")
                st.markdown("次のステップ3で品質分析を実行できます →")
                st.markdown('</div>', unsafe_allow_html=True)

    # ========== タブ3: 品質・用語分析 ==========
    with tab3:
        if not st.session_state.research_completed:
            st.warning("⚠️ まずステップ2でリサーチを実行してください")
        else:
            project_name = st.session_state.current_project

            # 品質検証
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.markdown("### 🔍 品質検証")
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("🔍 品質検証開始", key="start_quality"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("🔄 品質検証を実行中...")
                progress_bar.progress(20)

                cmd = [
                    sys.executable,
                    "course_quality_validator.py",
                    "--web-research", str(OUTPUTS_DIR / f"{project_name}_web.json"),
                    "--youtube-research", str(OUTPUTS_DIR / f"{project_name}_youtube.json"),
                    "--output", str(OUTPUTS_DIR / f"{project_name}_quality.json")
                ]

                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd=Path(__file__).parent
                    )

                    progress_bar.progress(100)

                    if result.returncode == 0:
                        st.session_state.quality_completed = True
                        status_text.empty()
                        st.success("✅ 品質検証完了！")
                    else:
                        st.error("❌ エラーが発生しました")
                        st.code(result.stderr)

                except Exception as e:
                    st.error(f"❌ エラー: {str(e)}")

            # 品質レポート表示
            quality_file = OUTPUTS_DIR / f"{project_name}_quality.json"
            if quality_file.exists():
                with open(quality_file, 'r', encoding='utf-8') as f:
                    quality_data = json.load(f)

                # 品質評価
                quality = quality_data.get('overall_quality', 'unknown')
                quality_colors = {
                    'excellent': '🌟',
                    'good': '✅',
                    'acceptable': '⚠️',
                    'needs_improvement': '❌'
                }
                quality_labels = {
                    'excellent': '優秀',
                    'good': '良好',
                    'acceptable': '許容範囲',
                    'needs_improvement': '改善必要'
                }

                icon = quality_colors.get(quality, '❓')
                label = quality_labels.get(quality, '不明')

                st.markdown(f"### {icon} 総合品質: {label}")

                # メトリクス
                summary = quality_data.get('integrated_summary', {})
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("総情報源", summary.get('total_information_sources', 0))
                with col2:
                    st.metric("データポイント", summary.get('total_data_points', 0))
                with col3:
                    st.metric("信頼性の高い情報源", summary.get('credible_sources', 0))

                # 推奨事項
                with st.expander("💡 推奨事項を見る"):
                    for rec in quality_data.get('quality_recommendations', []):
                        st.write(f"• {rec}")

            st.markdown("---")

            # 用語分析
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.markdown("### 📖 用語分析")
            st.markdown('</div>', unsafe_allow_html=True)

            course_theme = st.text_input(
                "講座テーマ（オプション）",
                placeholder="例: ChatGPT業務活用",
                key="course_theme_input"
            )

            if st.button("📖 用語分析開始", key="start_terminology"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("🔄 用語分析を実行中...")
                progress_bar.progress(20)

                cmd = [
                    sys.executable,
                    "course_terminology_analyzer.py",
                    "--web-research", str(OUTPUTS_DIR / f"{project_name}_web.json"),
                    "--youtube-research", str(OUTPUTS_DIR / f"{project_name}_youtube.json"),
                    "--output", str(OUTPUTS_DIR / f"{project_name}_terminology.json")
                ]

                if course_theme:
                    cmd.extend(["--course-theme", course_theme])

                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd=Path(__file__).parent
                    )

                    progress_bar.progress(100)

                    if result.returncode == 0:
                        st.session_state.terminology_completed = True
                        status_text.empty()
                        st.success("✅ 用語分析完了！")
                    else:
                        st.error("❌ エラーが発生しました")
                        st.code(result.stderr)

                except Exception as e:
                    st.error(f"❌ エラー: {str(e)}")

            # 用語レポート表示
            terminology_file = OUTPUTS_DIR / f"{project_name}_terminology.json"
            if terminology_file.exists():
                with open(terminology_file, 'r', encoding='utf-8') as f:
                    terminology_data = json.load(f)

                summary = terminology_data.get('terminology_summary', {})

                # メトリクス
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("ユニーク用語数", summary.get('total_unique_terms', 0))
                with col2:
                    st.metric("トップ用語数", summary.get('top_terms_count', 0))

                # トップ10用語
                top_terms = terminology_data.get('top_terms', [])[:10]
                if top_terms:
                    st.markdown("#### 🔝 重要用語トップ10")

                    # テーブルで表示
                    df = pd.DataFrame([
                        {
                            "順位": i+1,
                            "用語": term['term'],
                            "頻度": term['frequency'],
                            "カテゴリ": term['category'],
                            "学習フェーズ": term.get('learning_phase', 'unknown')
                        }
                        for i, term in enumerate(top_terms)
                    ])
                    st.dataframe(df, use_container_width=True)

                # 推奨事項
                with st.expander("💡 推奨事項を見る"):
                    for rec in terminology_data.get('recommendations', []):
                        st.write(f"• {rec}")

    # ========== タブ4: 講座設定 ==========
    with tab4:
        if not st.session_state.research_completed:
            st.warning("⚠️ まずステップ2でリサーチを実行してください")
        else:
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.markdown("### ⚙️ 講座の詳細設定")
            st.markdown('</div>', unsafe_allow_html=True)

            # CSVから講座リストを取得
            csv_path = Path(__file__).parent / "自動R7.11 講座計画表.csv"
            if csv_path.exists():
                try:
                    df = pd.read_csv(csv_path, usecols=range(6), dtype=str)
                    df.columns = ['category', 'course', 'unit_no', 'unit_name', 'slide_no', 'slide_title']
                    df = df.dropna(subset=['course'])
                    df = df[df['course'] != '講座名']
                    courses = df['course'].unique().tolist()
                except:
                    courses = []
            else:
                courses = []

            with st.form("course_config_form"):
                course_name = st.selectbox(
                    "📚 講座名",
                    courses if courses else ["講座計画表が見つかりません"],
                    key="course_name"
                )

                unit_number = st.text_input(
                    "📑 ユニット番号（オプション）",
                    placeholder="例: 1",
                    key="unit_number"
                )

                learner_profile = st.text_area(
                    "👥 受講者像",
                    placeholder="例: ChatGPTを業務で使いたいビジネスパーソン",
                    key="learner_profile"
                )

                target_behavior = st.text_area(
                    "🎯 到達目標（ゴール行動）",
                    placeholder="例: ChatGPTを適切に活用して業務効率を向上できる",
                    key="target_behavior"
                )

                col1, col2 = st.columns(2)
                with col1:
                    duration = st.selectbox(
                        "⏱️ 想定時間",
                        ["10分", "15分", "20分", "30分", "45分", "60分"],
                        index=3,
                        key="duration"
                    )

                with col2:
                    tone = st.selectbox(
                        "🎨 トーン＆マナー",
                        [
                            "親しみやすく、実践的なトーン",
                            "丁寧で専門的なトーン",
                            "カジュアルで楽しいトーン",
                            "ビジネスライクで効率的なトーン"
                        ],
                        key="tone"
                    )

                submitted = st.form_submit_button("💾 設定を保存", type="primary")

                if submitted:
                    if not learner_profile or not target_behavior:
                        st.error("受講者像と到達目標は必須です")
                    else:
                        # セッションに保存
                        st.session_state.course_config = {
                            "course_name": course_name,
                            "unit_number": unit_number if unit_number else None,
                            "learner_profile": learner_profile,
                            "target_behavior": target_behavior,
                            "duration": duration,
                            "tone": tone
                        }
                        st.success("✅ 設定を保存しました！")
                        st.markdown("次のステップ5でプロンプトを生成できます →")

    # ========== タブ5: プロンプト生成 ==========
    with tab5:
        if not st.session_state.research_completed:
            st.warning("⚠️ まずステップ2でリサーチを実行してください")
        elif 'course_config' not in st.session_state:
            st.warning("⚠️ まずステップ4で講座設定を保存してください")
        else:
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.markdown("### 📝 Gemini用プロンプト生成")
            st.markdown('</div>', unsafe_allow_html=True)

            project_name = st.session_state.current_project
            config = st.session_state.course_config

            # 設定内容の確認
            with st.expander("⚙️ 設定内容を確認"):
                st.write(f"**講座名**: {config['course_name']}")
                if config['unit_number']:
                    st.write(f"**ユニット**: {config['unit_number']}")
                st.write(f"**受講者像**: {config['learner_profile']}")
                st.write(f"**到達目標**: {config['target_behavior']}")
                st.write(f"**想定時間**: {config['duration']}")
                st.write(f"**トーン**: {config['tone']}")

            if st.button("🚀 プロンプト生成", key="generate_prompt", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("🔄 プロンプトを生成中...")
                progress_bar.progress(20)

                # course_plan_parser.py を実行
                cmd = [
                    sys.executable,
                    "course_plan_parser.py",
                    "--csv", "自動R7.11 講座計画表.csv",
                    "--course", config['course_name'],
                    "--format", "canvas-script",
                    "--learner_profile", config['learner_profile'],
                    "--target_behavior", config['target_behavior'],
                    "--duration", config['duration'],
                    "--tone", config['tone'],
                    "--web-research", str(OUTPUTS_DIR / f"{project_name}_web.json"),
                    "--youtube-research", str(OUTPUTS_DIR / f"{project_name}_youtube.json")
                ]

                if config['unit_number']:
                    cmd.extend(["--unit", config['unit_number']])

                # 品質・用語レポートがあれば追加
                quality_file = OUTPUTS_DIR / f"{project_name}_quality.json"
                terminology_file = OUTPUTS_DIR / f"{project_name}_terminology.json"

                if quality_file.exists():
                    cmd.extend(["--quality-report", str(quality_file)])

                if terminology_file.exists():
                    cmd.extend(["--terminology-report", str(terminology_file)])

                try:
                    progress_bar.progress(50)
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd=Path(__file__).parent
                    )

                    progress_bar.progress(100)

                    if result.returncode == 0:
                        st.session_state.prompt_generated = True
                        st.session_state.generated_prompt = result.stdout

                        # プロンプトをファイルに保存
                        prompt_file = OUTPUTS_DIR / f"{project_name}_prompt.txt"
                        with open(prompt_file, 'w', encoding='utf-8') as f:
                            f.write(result.stdout)

                        status_text.empty()
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.markdown("### ✅ プロンプト生成完了！")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error("❌ エラーが発生しました")
                        st.code(result.stderr)

                except Exception as e:
                    st.error(f"❌ エラー: {str(e)}")

            # 生成されたプロンプトを表示
            if st.session_state.prompt_generated and hasattr(st.session_state, 'generated_prompt'):
                st.markdown("---")
                st.markdown("### 📄 生成されたプロンプト")

                # アクションボタン
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        label="💾 ダウンロード",
                        data=st.session_state.generated_prompt,
                        file_name=f"{project_name}_gemini_prompt.txt",
                        mime="text/plain",
                        key="download_prompt"
                    )
                with col2:
                    if st.button("📋 クリップボードにコピー", key="copy_prompt"):
                        st.info("テキストを選択してコピーしてください（Ctrl+A, Ctrl+C）")
                with col3:
                    st.link_button("🤖 Geminiで開く", "https://gemini.google.com/")

                # プロンプト表示（スクロール可能）
                with st.container():
                    st.text_area(
                        "プロンプト内容",
                        st.session_state.generated_prompt,
                        height=400,
                        key="prompt_display"
                    )

# フッター
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
    📚 講座自動化システム v1.0 |
    Made with ❤️ using Streamlit |
    データ保存先: data/
    </div>
    """,
    unsafe_allow_html=True
)
