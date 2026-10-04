#===== 【さやねー】登録時の自動打刻追記 =====
from datetime import date
#===== 【さやねー】追加ここまで =====
import streamlit as st
from llm.tools import generate_keywords
#===== 【さやねー】いささん作業：find_similar(case: dict, top_k=3)を呼び出す設計（後で↓頭の＃を外す） =====
from services.similar import find_similar
#===== 【さやねー】追加ここまで =====

st.set_page_config(
    page_title="テクゼロン電気　お客さまナレッジデータベース",
    page_icon="📝",
    layout="wide",
)

st.title("テクゼロン電気　お客さまナレッジデータベース")
st.write("振り返りしたい接客事例について登録するアプリです。あわせて過去の類似接客事例も確認しましょう。")
st.info("登録したい接客体験を入力してください。入力作業の後、ＤＢから成功事例を検索・表示・確認することができます。")

# タブ作成
tab_register, tab_search = st.tabs(["事例登録", "ナレッジ検索"])

# ===== 【飯酒盃】キーワード生成・類似事例 ここから =====
#===== 【さやねー】操作のため一時的にいささん作成内容を削除 =====

# ===== 【飯酒盃】キーワード生成・類似事例 ここまで =====           


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
        ["選択してください", "田中 太郎", "山田 花子", "佐藤 健一"]
    )

    # 商品カテゴリ選択（No.2 入力フォーム）
    selected_category = st.selectbox(
        "商品カテゴリ",
        ["選択してください", "エアコン", "冷蔵庫", "洗濯機"]
    )

    # 結果選択
    selected_result = st.selectbox(
        "結果",
        ["選択してください", "成約", "検討", "失注"]
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
# 類似事例を探して保存する（ここまでがボタンの中）
        # DB に接続できないなどで失敗しても、画面全体は止めずにメッセージを出す（NF-04）
        # ===== 【飯酒盃】AIキーワード生成（No.6） ここから =====
        # 入力内容から AI が検索用キーワードを作る。失敗しても空のリストが返るだけで、処理は止まらない
        with st.spinner("AIがキーワードを作成しています..."):
            st.session_state.case_data["keywords"] = generate_keywords(
                case_text="\n".join([
                    f"顧客属性：{customer_attribute}",
                    f"顧客ニーズ：{customer_needs}",
                    f"提案内容：{proposal}",
                ]),
                category=selected_category,
                result=selected_result,
            )
        # ===== 【飯酒盃】AIキーワード生成 ここまで =====

        try:
            with st.spinner("類似事例を探しています..."):
                st.session_state.similar_cases = find_similar(st.session_state.case_data, top_k=3)
            st.session_state.similar_error = None
        except RuntimeError as error:
            # database.py が出す「事例を取得できませんでした」などのメッセージをそのまま表示する
            st.session_state.similar_cases = []
            st.session_state.similar_error = str(error)
        except Exception:
            st.session_state.similar_cases = []
            st.session_state.similar_error = "類似事例を表示できませんでした。時間をおいてもう一度お試しください。"
        # 新しく探したときは、最初の1件だけ表示する状態に戻す
        st.session_state.show_all_similar = False

    # ===== 【飯酒盃】類似事例の表示（最初は1件、「他の事例を見る」で最大3件） ここから =====
    # ボタンの外なので、保存されたデータがあれば再実行のたびに表示される
    keywords = st.session_state.case_data.get("keywords") if st.session_state.case_data else None
    if keywords:
        st.markdown("**AIが付けたキーワード：** " + " ".join(f"`{k}`" for k in keywords))
    elif st.session_state.case_data:
        st.caption("AIキーワードを作成できませんでした（キーワードなしで類似事例を探しています）。")

    if st.session_state.get("similar_error"):
        # 取得に失敗したときは「見つからなかった」と区別して、エラーとして表示する
        st.error(st.session_state.similar_error)
    elif st.session_state.similar_cases:
        st.subheader("類似事例")
        show_all = st.session_state.get("show_all_similar", False)
        shown_cases = st.session_state.similar_cases if show_all else st.session_state.similar_cases[:1]
        for case in shown_cases:
            with st.expander(case["title"]):
                st.write(case["detail"])

        # まだ表示していない事例があるときだけ、ボタンを出す
        rest = len(st.session_state.similar_cases) - len(shown_cases)
        if rest > 0 and st.button(f"他の事例を見る（あと{rest}件）"):
            st.session_state.show_all_similar = True
            st.rerun()
    elif st.session_state.case_data:
        st.info("似ている過去事例は見つかりませんでした。")
    # ===== 【飯酒盃】類似事例の表示 ここまで =====

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
                "report_date": date.today().isoformat(),
                # 【飯酒盃】「類似事例を見る」で AI が作ったキーワード（未実行なら空）
                "keywords": st.session_state.case_data.get("keywords", []),
            }

            st.success("事例データをまとめました。")
            st.write(data)

            # 仮の登録処理
            st.success("事例を登録しました！")


#===== 【さやねー】入力フォーム ここまで =====

# =====【いっさん】検索タブ ここから =====
from services.database import get_categories, get_report_years
from services.search import search_knowledge

def render_search_tab():
    st.subheader("ナレッジ検索")
    st.caption("検索語を入力してください。複数語はスペースで区切ります（AND検索）。")

    try:
        #  入力欄に並べる選択肢をDBから準備する。
        categories = get_categories()
        years = get_report_years()
    except RuntimeError as error:
        st.error(str(error))
        return

    # カテゴリIDから名称を引く辞書を作る（DBにIDを渡し、画面に名称を返す）
    category_names = {row["id"]: row["name"] for row in categories}
    # フォーム内の入力をまとめ、検索ボタンで送信する
    with st.form("knowledge_search_form"):
        query = st.text_input(
            "フリーワード（必須）",
            placeholder="例：省エネ 30代",
            key="knowledge_search_query",
        )
        # 左にカテゴリ、右に報告年を配置。
        left, right = st.columns(2)
        with left:
            #  Noneはすべての選択肢として加え、その後ろにカテゴリIDを並べる。
            category_id = st.selectbox(
                "商品カテゴリ",
                [None, *category_names],
                format_func=lambda value: "すべて" if value is None else category_names[value],
                key = "knowledge_search_category",
            )
        with right:
            # 年の値は整数として保持し、画面表示だけ「2026年」の形にする。
            # Noneはすべてで、年を絞らないことを示す。
            year = st.selectbox(
                "報告年",
                [None, *years],
                format_func=lambda value: "すべて" if value is None else f"{value}年",
                key="knowledge_search_year",
            )
        submitted = st.form_submit_button("検索", type = "primary")

    # 検索ボタンを押したときだけこの中の処理を実行。条件を確認し、問題なければ検索関数へ入力値を渡す。
    if submitted:
        #  空入力や失敗時に、前回の結果を今回の結果として残さない
        st.session_state["knowledge_search_output"] = None
        if not query.strip():
            st.warning("フリーワードを入力してください。")
        else:
            try:
                with st.spinner("検索しています..."):
                    results = search_knowledge(query, category_id, year)
                # 検索条件と結果をまとめて保存する。st.session_stateへ残して次回も結果を表示できるようにする。
                st.session_state["knowledge_search_output"] = {
                    "query": query,
                    "category": category_names.get(category_id, "すべて"),
                    "year": year,
                    "results": results,
                }
            except RuntimeError as error:
                st.error(str(error))

    # 保存しておいた直近の検索結果を取り出す。
    # 初回表示や検索失敗後はNoneなので、結果の表示処理へ進まず戻る。
    output = st.session_state.get("knowledge_search_output")
    if output is None:
        return

    # フォーム編集後も、結果がどの検索条件のものかわかるようにする。
    year_label = f"{output['year']}年" if output["year"] is not None else "すべて"
    st.text(
        f"検索語：{output['query']} ／ カテゴリ：{output['category']} ／ 報告年：{year_label}"
    )
    results = output["results"]
    st.caption(f"表示：{len(results)}件（関連度順・最大20件）")
    # 検索結果が0件の時の案内（処理失敗とは別）
    if not results:
        st.info("該当する事例がありません。検索語を減らすか、絞り込み条件を変更してください。")
        return

    # 検索結果を1件ずつ表示する。
    for number, record in enumerate(results, 1):
        with st.container(border=True):
            st.text(f"{number}. 報告日：{record.get('report_date') or '未設定'}")
            # タグ風の表示
            # カテゴリ名・検索結果・キーワードを1つのリストへまとめる
            tag_names = [
                record.get("category_name") or "カテゴリ未設定",
                record.get("result_name") or "結果未設定",
            ] + record["keywords"]
            tags = []
            for tag in tag_names:
                # データ内の記号・改行でタグの表示が崩れるのを防ぐ
                tag = tag.replace("`", "").replace("\n", " ").replace("\r", " ")
                tags.append(f"`{tag}")
            st.markdown(" ".join(tags))
            st.text(record["preview"] or "本文なし")
            # クリックで開閉できる領域を作り、事例の全文を表示する。
            with st.expander("詳細を見る"):
                st.text(f"投稿者：{record.get('user_name') or '未設定'}")
                for label, field in [
                    ("顧客属性", "customer_attribute"),
                    ("顧客ニーズ", "customer_needs"),
                    ("提案内容", "proposal"),
                    ("振り返り", "reflection")
                ]:
                    st.markdown(f"**{label}**")
                    st.text(record.get(field) or "未入力")

with tab_search:
    render_search_tab()
# =====【いっさん】検索タブ ここまで =====