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

# ===== 【飯酒盃】キーワード生成・類似事例 ここから =====
# OpenAI API接続確認（後で消す）
with tab_test:
    st.subheader("AIキーワード生成テスト")
    # secrets.toml からAPIキーを取得
    client = OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
    )

    # 入力欄
    user_message = st.text_area(
        "接客事例を入力してください",
        placeholder="例：40代夫婦のお客様。冷蔵庫を探していて、容量は大きい方がいいが、電気代も気にしていた。省エネ性能を説明して、500Lの商品を提案した。")

    if user_message:

        try:
        #  キーワード生成用プロンプト
            prompt = f"""
            以下の接客事例から、検索に役立つ重要なキーワードを抽出してください。
            【ルール】
            - キーワードは最大5個
            - 短い言葉で表現する
            - 顧客属性、顧客ニーズ、商品・サービス、提案内容などを優先する
            - キーワードだけをカンマ区切りで出力する
            - 説明文は不要

            【接客事例】
            {user_message}
"""     
            # OpenAI APIへ送信
            response = client.responses.create(
                model="gpt-5-nano",
                input=prompt,
            )

            # AIの回答を表示
            st.subheader("AIが生成したキーワード")
            st.write(response.output_text)

        except Exception as e:
            st.error("OpenAI APIへの接続に失敗しました")
            st.code(str(e))
            