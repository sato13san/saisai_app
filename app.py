import streamlit as st
from openai import OpenAI

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

# OpenAI API接続確認（後で消す）
with tab_test:
    st.subheader("AIチャット 接続テスト")
    # secrets.toml からAPIキーを取得
    client = OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
    )

    # 入力欄
    user_message = st.chat_input("メッセージを入力してください")

    if user_message:

        # ユーザーのメッセージを表示
        with st.chat_message("user"):
            st.write(user_message)

        try:
            # OpenAI APIへ送信
            response = client.responses.create(
                model="gpt-5-nano",
                input=user_message,
            )

            # AIの回答を表示
            with st.chat_message("assistant"):
                st.write(response.output_text)

        except Exception as e:
            st.error("OpenAI APIへの接続に失敗しました")
            st.code(str(e))