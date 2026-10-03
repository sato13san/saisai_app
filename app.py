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
tab_register, tab_search = st.tabs(["事例登録", "ナレッジ検索"])

# ===== 【飯酒盃】キーワード生成・類似事例 ここから =====
#===== 【さやねー】操作のため一時的にいささん作成内容を削除 =====

# ===== 【飯酒盃】キーワード生成・類似事例 ここまで =====           


# ===== 【いっさん】Supabase接続確認（後で消す） =====
import streamlit as st
from supabase import create_client

# Supabase接続情報を取得
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]

# Supabaseクライアントを作成
supabase = create_client(supabase_url, supabase_key)

st.title("Supabase 接続テスト")

try:
    # usersテーブルから1件だけ取得
    response = (
        supabase
        .table("users")
        .select("*")
        .limit(1)
        .execute()
    )

    st.success("✅ Supabaseへの接続に成功しました！")

    st.write("取得結果")
    st.write(response.data)

except Exception as e:
    st.error("❌ Supabaseへの接続に失敗しました")
    st.write(e)
# ===== 【いっさん】Supabase接続確認（ここまで） =====
# ===== 【さやねー】入力フォーム ここから =====
# ここにこれから事例登録画面を作っていきます
with tab_register:
    st.header("事例登録")
    st.write("接客事例を入力してください")
# ユーザー選択
    selected_user = st.selectbox(
        "ユーザー",
        ["選択してください", "ユーザーA", "ユーザーB", "ユーザーC"]
    )
# 商品カテゴリ選択
    selected_category = st.selectbox(
        "商品カテゴリ",
        ["選択してください", "冷蔵庫", "洗濯機", "テレビ", "エアコン"]
    )
# 結果選択
    selected_result = st.selectbox(
        "結果",
        ["選択してください", "成約", "未成約"]
    )
# 顧客属性
    customer_attribute = st.text_area(
        "顧客属性",
        placeholder="例：40代夫婦、子ども2人"
    )
 # 顧客ニーズ
    customer_needs = st.text_area(
        "顧客ニーズ",
        placeholder="例：容量の大きい冷蔵庫が欲しい。電気代も抑えたい。"
    )
# 顧客ニーズ
    customer_needs = st.text_area(
        "顧客ニーズ",
        placeholder="例：容量の大きい冷蔵庫が欲しい。電気代も抑えたい。"
    )
# ===== 【さやねー】入力フォーム ここまで =====