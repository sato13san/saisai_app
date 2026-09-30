import streamlit as st
from llm.tools import generate_keywords

st.set_page_config(
    page_title="saisaiアプリ",
    page_icon="📝",
    layout="wide",
)

st.title("saisaiアプリ")
st.write("Hello world")
st.info("開発環境のセットアップが完了しました！")

# タブ作成
tab_test, tab_search, tab_crawl, tab_list = st.tabs(['AIテスト', '検索', 'クロール', '一覧'])

# ===== 【飯酒盃】キーワード生成・類似事例 ここから =====
# OpenAI API接続確認（後で消す）
with tab_test:
    st.subheader("AIキーワード生成テスト")

    # 入力欄
    user_message = st.text_area(
        "接客事例を入力してください",
        placeholder="例：40代夫婦のお客様。冷蔵庫を探していて、容量は大きい方がいいが、電気代も気にしていた。省エネ性能を説明して、500Lの商品を提案した。")

    if user_message:
            keywords = generate_keywords(
                case_text=user_message
    )


            # AIの回答を表示
            st.subheader("AIが生成したキーワード")
            st.write(keywords)
# ===== 【飯酒盃】キーワード生成・類似事例 ここまで =====           