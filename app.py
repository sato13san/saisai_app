#===== 【さやねー】登録時の自動打刻追記 =====
from datetime import date
#===== 【さやねー】追加ここまで =====
import streamlit as st
from llm.tools import generate_keywords
#===== 【さやねー】いささん作業：find_similar(case: dict, top_k=3)を呼び出す設計（後で↓頭の＃を外す） =====
#from services.similar import find_similar
#===== 【さやねー】追加ここまで =====

st.set_page_config(
    page_title="テクゼロン電気　お客さまナレッジデータベース",
    page_icon="📝",
    layout="wide",
)

st.title("テクゼロン電気　お客さまナレッジデータベース")
st.write("また、振り返りしたい接客事例について、過去の類似接客事例を確認しましょう。")
st.info("登録したい接客体験を入力してください。入力作業の後、ＤＢから成功事例を検索・表示・確認することができます。")

# タブ作成
tab_register, tab_search = st.tabs(["事例登録", "ナレッジ検索"])

# ===== 【飯酒盃】キーワード生成・類似事例 ここから =====
#===== 【さやねー】操作のため一時的にいささん作成内容を削除 =====

# ===== 【飯酒盃】キーワード生成・類似事例 ここまで =====           


# ===== 【いっさん】Supabase接続確認（後で消す） =====
#===== 【さやねー】supabase接続確認を消しました。 =====

# ===== 【いっさん】Supabase接続確認（ここまで） =====

# ===== 【さやねー】入力フォームをここから作っていきます =====
# 事例登録画面を作っていきます
with tab_register:
    st.header("事例登録")

    # 入力時の注意
    st.info(
        "※顧客の氏名・電話番号・住所などの個人情報は入力しないでください。"
    )
    
# 入力した事例を保存する入れ物
    if "case_data" not in st.session_state:
        st.session_state.case_data = {}

# 類似事例を保存する入れ物
    if "similar_cases" not in st.session_state:
        st.session_state.similar_cases = []

    st.write("接客事例を入力してください")
# ユーザー選択（No.1 ユーザー選択）
    selected_user = st.selectbox(
        "ユーザー",
        ["選択してください", "ユーザーA", "ユーザーB", "ユーザーC"]
    )
# 商品カテゴリ選択（No.2 入力フォーム）
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
# 提案内容
    proposal = st.text_area(
        "提案内容",
        placeholder="例：500Lの省エネ性能の高い冷蔵庫を提案した。"
    )

 # 類似事例を見るボタン（No.4 類似事例詳細表示）
    if st.button("類似事例を見る"):
        st.session_state.case_data = {
            "user": selected_user,
            "category": selected_category,
            "result": selected_result,
            "customer_attribute": customer_attribute,
            "customer_needs": customer_needs,
            "proposal": proposal
        }

        st.success("入力内容を保存しました。")
#　いささんデータつなぎ後に稼働するところ
        # 保存した事例データを確認
        st.write("保存した事例データ")
        st.write(st.session_state.case_data)
# 今回の事例
        st.subheader("今回の事例")

        st.write(
            f"商品カテゴリ：{st.session_state.case_data['category']}"
        )

        st.write(
            f"結果：{st.session_state.case_data['result']}"
        )

        st.write(
            f"顧客ニーズ：{st.session_state.case_data['customer_needs']}"
        )

        st.write(
            f"提案内容：{st.session_state.case_data['proposal']}"
        )
# 仮の類似事例（後でいささんデータつなぎ後に修正が必要なパート）将来一行下を　find_similar(case_data, top_k=3)に置き換える　
st.session_state.similar_cases = [
            {
                "title": "冷蔵庫の容量と省エネを重視した事例",
                "detail": "40代夫婦のお客様に500Lクラスの省エネ冷蔵庫を提案した事例です。"
            },
            {
                "title": "家族構成に合わせて冷蔵庫を提案した事例",
                "detail": "子どもがいるご家庭に、容量と使いやすさを重視して提案した事例です。"
            },
            {
                "title": "電気代を重視した冷蔵庫の提案例",
                "detail": "ランニングコストを気にされるお客様に、省エネ性能を説明した事例です。"
            }
        ]
# 類似事例を表示
st.subheader("類似事例")
for case in st.session_state.similar_cases:
            with st.expander(case["title"]):
                st.write(case["detail"])

# 振り返り入力（No.5 振り返り入力・事例登録）
st.subheader("振り返り")
# いっさん作業　create_knowledge(data: dict, keywords: list[str]) -> str　がつながるまでの仮入力
reflection = st.text_area(
        "今回の接客を振り返って、気づいたことや次回に活かしたいことを入力してください。",
        placeholder="例：お客様の家族構成をもう少し詳しく聞いてから、容量を提案するとよかった。"
    )
# 事例登録ボタン
if st.button("事例を登録する"):

        # 必須項目の入力チェック
        if selected_user == "選択してください":
            st.warning("ユーザーを選択してください。")

        elif selected_category == "選択してください":
            st.warning("商品カテゴリを選択してください。")

        elif selected_result == "選択してください":
            st.warning("結果を選択してください。")

        else:
            # 登録する事例データをまとめる
            data = {
                "user": selected_user,
                "category": selected_category,
                "result": selected_result,
                "customer_attribute": customer_attribute,
                "customer_needs": customer_needs,
                "proposal": proposal,
                "reflection": reflection,
                "report_date": date.today().isoformat()
            }

            st.success("事例データをまとめました。")
            st.write(data)

            # 仮の登録処理
            st.success("事例を登録しました！")


#===== 【さやねー】入力フォーム ここまで =====