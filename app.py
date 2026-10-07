#===== 【さやねー】登録時の自動打刻追記 =====
from datetime import date
#===== 【さやねー】追加ここまで =====
import streamlit as st
from llm.tools import generate_keywords
#===== 【さやねー】いささん作業：find_similar(case: dict, top_k=3)を呼び出す設計（後で↓頭の＃を外す） =====
from services.similar import find_similar
from services.database import get_users, get_categories, get_results, create_knowledge
from services.check import find_other_categories
#===== 【さやねー】追加ここまで =====
#===== 【いさ】エラーチェック =====
from services.database import get_users, get_categories, get_results, create_knowledge
from services.check import find_other_categories
#===== 【いさ】追加ここまで =====

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

#===== 【さやねー】冒頭3問を横並びにする =====
    st.write("接客事例を入力してください")

    # ユーザー・カテゴリ・結果の選択肢をDBから取得
    try:
        user_ids = {row["name"]: row["id"] for row in get_users()}
        category_ids = {row["name"]: row["id"] for row in get_categories()}
        result_ids = {row["name"]: row["id"] for row in get_results()}
    except RuntimeError as error:
        st.error(str(error))
        st.stop()

    # ユーザー・商品カテゴリ・結果を横並びに表示
    col_user, col_category, col_result = st.columns(3)

    with col_user:
        selected_user = st.selectbox(
            "ユーザー",
            ["選択してください", *user_ids]
        )

    with col_category:
        selected_category = st.selectbox(
            "商品カテゴリ",
            ["選択してください", *category_ids]
        )

    with col_result:
        selected_result = st.selectbox(
            "結果",
            ["選択してください", *result_ids]
        )
    
    # 報告日
    report_date = st.date_input(
    "報告日",
    value=date.today()
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
        with st.spinner("キーワード生成中..."):
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

    # ===== 【飯酒盃】カテゴリと内容の食い違いチェック（No.3） ここから =====
    # 入力内容のカテゴリと内容が食い違っていないかをチェック
    others = find_other_categories(
        st.session_state.case_data.get("category", ""),
        st.session_state.case_data.get("customer_needs", "") + 
    st.session_state.case_data.get("proposal", "")
    )
    if others:
        st.warning(f"注意！入力内容に「{'・'.join(others)}」に関する言葉があります。"
               f"商品カテゴリは「{st.session_state.case_data['category']}」で合っていますか？")
    # ===== 【飯酒盃】カテゴリと内容の食い違いチェック ここまで =====

    # ===== 【飯酒盃】類似事例の表示（最初は1件、「他の事例を見る」で最大3件） ここから =====
    # ボタンの外なので、保存されたデータがあれば再実行のたびに表示される
    keywords = st.session_state.case_data.get("keywords") if st.session_state.case_data else None
    if keywords:
        st.markdown("**生成されたキーワード：** " + " ".join(f"`{k}`" for k in keywords))
    elif st.session_state.case_data:
        st.caption("キーワードを生成できませんでした（キーワードなしで類似事例を探しています）。")

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
    #===== 【さやねー】事例登録時に誤りがあった場合の選択ボタンセット =====

    # 登録確認画面の初期状態
    if "show_register_confirmation" not in st.session_state:
        st.session_state.show_register_confirmation = False
    # 確認画面のときだけボタンを表示
    if st.session_state.show_register_confirmation:


        # 確認画面のボタン
        col_back, col_register = st.columns(2)

        with col_back:
            if st.button("戻って修正"):
                st.session_state.show_register_confirmation = False
                st.rerun()

        with col_register:
            if st.button("この内容で登録する", type="primary"):

                # DBに保存するデータを作成
                data = {
                    "user_id": user_ids[selected_user],
                    "product_category_id": category_ids[selected_category],
                    "result_id": result_ids[selected_result],
                    "customer_attribute": customer_attribute,
                    "customer_needs": customer_needs,
                    "proposal": proposal,
                    "reflection": reflection,
                    "report_date": report_date.isoformat(),
                }

                # 「類似事例を見る」で生成したキーワードを取得
                keywords = st.session_state.case_data.get("keywords", [])

                try:
                    with st.spinner("登録しています..."):
                        knowledge_id = create_knowledge(data, keywords)

                    st.success("事例を登録しました！")

                except RuntimeError as error:
                    st.error(str(error))

    # 登録確認画面を表示するための状態
    if "show_register_confirmation" not in st.session_state:
        st.session_state.show_register_confirmation = False
    #===== 【さやねー】事例登録時に誤りがないかのアラート表示追加 =====

    # 確認画面を表示していないときだけ「事例を登録する」を表示
    if not st.session_state.show_register_confirmation:
        if st.button("事例を登録する", type="primary"):

            # 必須項目の入力チェック
            if selected_user == "選択してください":
                st.warning("ユーザーを選択してください。")

            elif selected_category == "選択してください":
                st.warning("商品カテゴリを選択してください。")

            elif selected_result == "選択してください":
                st.warning("結果を選択してください。")

            else:
                st.session_state.show_register_confirmation = True
                st.rerun()

    # 登録内容の確認
    if st.session_state.show_register_confirmation:
        st.subheader("登録内容の確認")

        st.write(f"**ユーザー：** {selected_user}")
        st.write(f"**商品カテゴリ：** {selected_category}")
        st.write(f"**結果：** {selected_result}")
        st.write(f"**報告日：** {report_date}")
        st.write(f"**顧客属性：** {customer_attribute}")
        st.write(f"**顧客ニーズ：** {customer_needs}")
        st.write(f"**提案内容：** {proposal}")
        st.write(f"**振り返り：** {reflection}")



    #===== 【さやねー】入力フォーム ここまで =====

# =====【いっさん】検索タブ ここから =====
from services.database import get_categories, get_report_years
from services.search import search_knowledge

# 検索結果の保存先を1か所で定義する。以前と同じキーなので保持方法は変わらない。
SEARCH_OUTPUT_KEY = "knowledge_search_output"

with tab_search:
    st.subheader("ナレッジ検索")
    st.caption("検索語を入力してください。複数語はスペースで区切ります（OR検索）。")  # AND検索からOR検索に変更

    try:
        #  入力欄に並べる選択肢をDBから準備する。
        search_categories = get_categories()
        search_years = get_report_years()
    except RuntimeError as error:
        st.error(str(error))
    else:
        # try内の取得が成功したときだけ、検索フォームと結果を表示する。
        # 名前にsearch_を付け、登録タブで使う変数と区別する。
        search_category_names = {row["id"]: row["name"] for row in search_categories}

        # フォーム内の入力をまとめ、検索ボタンで送信する
        with st.form("knowledge_search_form"):
            search_query = st.text_input(
                "フリーワード（必須）",
                placeholder="例：省エネ 30代",
                key="knowledge_search_query",
            )
            search_left, search_right = st.columns(2)
            with search_left:
                # 画面には名前を表示し、検索処理にはカテゴリIDを渡す。
                search_category_id = st.selectbox(
                    "商品カテゴリ",
                    [None, *search_category_names],
                    format_func=lambda value: (
                        "すべて" if value is None else search_category_names[value]
                    ),
                    key="knowledge_search_category",
                )
            with search_right:
                # Noneは年で絞り込まないことを表す。表示だけ「2026年」の形にする。
                search_year = st.selectbox(
                    "報告年",
                    [None, *search_years],
                    format_func=lambda value: "すべて" if value is None else f"{value}年",
                    key="knowledge_search_year",
                )
            search_submitted = st.form_submit_button("検索", type="primary")

        # ③ 検索を実行し、検索条件と結果をまとめて保存する。
        if search_submitted:
            # 空入力や検索失敗のときに、以前の結果を今回の結果として残さない。
            st.session_state[SEARCH_OUTPUT_KEY] = None
            if not search_query.strip():
                st.warning("フリーワードを入力してください。")
            else:
                try:
                    with st.spinner("検索しています..."):
                        search_results = search_knowledge(
                            search_query, search_category_id, search_year
                        )
                except RuntimeError as error:
                    st.error(str(error))
                else:
                    st.session_state[SEARCH_OUTPUT_KEY] = {
                        "query": search_query,
                        "category": search_category_names.get(search_category_id, "すべて"),
                        "year": search_year,
                        "results": search_results,
                    }

        # ④ 保存済みの結果がある場合だけ表示する。
        # 初回はNone。検索成功で0件だった場合は辞書があるので、0件の案内を表示する。
        search_output = st.session_state.get(SEARCH_OUTPUT_KEY)
        if search_output is not None:
            search_year_label = (
                f"{search_output['year']}年" if search_output["year"] is not None else "すべて"
            )
            st.text(
                f"検索語：{search_output['query']} ／ "
                f"カテゴリ：{search_output['category']} ／ 報告年：{search_year_label}"
            )
            search_results = search_output["results"]
            st.caption(f"表示：{len(search_results)}件（関連度順・最大20件）")

            # 宿題と同じように、結果があれば1件ずつ表示する。
            if search_results:
                for i, page in enumerate(search_results, 1):
                    with st.container(border=True):
                        st.text(f"{i}. 報告日：{page.get('report_date') or '未設定'}")

                        # 商品カテゴリはラベル、接客結果は色付きの丸印と太字で表示する。
                        col_category, col_result = st.columns(2)
                        with col_category:
                            st.caption(f"📦 商品カテゴリ：{page.get('category_name') or '未設定'}")
                        with col_result:
                            result_name = page.get("result_name") or "未設定"
                            if result_name == "成約":
                                st.markdown("接客結果：**🟢 成約**")
                            elif result_name == "検討":
                                st.markdown("接客結果：**🟡 検討**")
                            elif result_name == "失注":
                                st.markdown("接客結果：**🔴 失注**")
                            else:
                                st.text(f"接客結果：{result_name}")

                        # キーワードだけをタグ風に表示する。
                        # 全件を表示し、未設定の場合はその旨を表示する。
                        keywords = page.get("keywords") or []
                        tags = []
                        for keyword in keywords:
                            keyword = keyword.replace("`", "").replace("\n", " ").replace("\r", " ")
                            if keyword.strip():
                                tags.append(f"`{keyword}`")
                        if tags:
                            st.markdown("🏷️ キーワード：" + " ".join(tags))
                        else:
                            st.caption("🏷️ キーワード：未設定")

                        # 概要と、クリックして開ける全文を表示する。
                        st.text(page["preview"] or "本文なし")
                        with st.expander("詳細を見る"):
                            st.text(f"投稿者：{page.get('user_name') or '未設定'}")
                            for label, field in [
                                ("顧客属性", "customer_attribute"),
                                ("顧客ニーズ", "customer_needs"),
                                ("提案内容", "proposal"),
                                ("振り返り", "reflection"),
                            ]:
                                st.markdown(f"**{label}**")
                                st.text(page.get(field) or "未入力")
            else:
                # OR検索では語を減らしても候補は増えないため、変更や絞り込み解除を案内する。
                st.info(
                    "該当する事例がありません。検索語を変えるか、"
                    "カテゴリ・報告年の絞り込みを解除してください。"
                )
# =====【いっさん】検索タブ ここまで =====