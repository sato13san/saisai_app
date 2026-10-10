import streamlit as st
from supabase import create_client

def get_client():
    """宿題のget_connection()に相当する、DB接続用の関数。"""
    try:
        # secrets.tomlから接続先とキーを読み、Supabaseを操作するための窓口を作る。
        # この時点では事例を取得しない。返された接続を、各取得関数で使う。
        supabase = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"],
        )
        return supabase
    except Exception:
        raise RuntimeError("Supabaseの接続URLとAPIキーを確認してください。") from None


def get_categories() -> list[dict]:
    """カテゴリのマスタを取得する。MVPの数種類のカテゴリを想定。"""
    # 接続用の関数を呼び出し、以降のtable・select等で使う変数へ入れる。
    supabase = get_client()
    try:
        # 取得するテーブル・列・条件を指定し、execute()で問い合わせを実行する。
        # 実行結果全体がresponse、その中のdataが取得した行のリストになる。
        response = (
            supabase
            .table("product_category")
            .select("id, name")
            .order("id")
            .execute()
        )
        # 取得した行を呼び出し元へ渡す。dataがNoneや空なら[]を返し、
        # 呼び出し元が常にリストとしてfor文などで扱えるようにする。
        return response.data or []
    except Exception:
        raise RuntimeError("商品カテゴリを取得できませんでした。") from None


def get_users() -> list[dict]:
    """ユーザーのマスタを取得する。登録画面のユーザー選択で使う。"""
    supabase = get_client()
    try:
        # get_categories と同じ形で、id と name のリストを返す。名前順に並べる。
        response = (
            supabase
            .table("users")
            .select("id, name")
            .order("name")
            .execute()
        )
        return response.data or []
    except Exception:
        raise RuntimeError("ユーザーを取得できませんでした。") from None


def get_results() -> list[dict]:
    """接客結果（成約・検討・失注）のマスタを取得する。登録画面の結果選択で使う。"""
    supabase = get_client()
    try:
        # get_categories と同じ形で、id と name のリストを返す。
        response = (
            supabase
            .table("result")
            .select("id, name")
            .order("id")
            .execute()
        )
        return response.data or []
    except Exception:
        raise RuntimeError("接客結果を取得できませんでした。") from None


def get_report_years() -> list[int]:
    """報告日から年を取り出し、新しい年から順に返す。"""
    # 接続用の関数を呼び出し、以降のtable・select等で使う変数へ入れる。
    supabase = get_client()
    # 年の選択肢を入れるリストを用意する。同じ年は後の処理で重複を除く。
    years = []
    # 何行目から取得するかを表す開始位置。最初は0行目から取得する。
    start = 0
    try:
        # 1回の取得上限を超える場合に備えて、取得を繰り返す。
        # 下の「if not rows」でデータが尽きたことを確認し、breakで終了する。
        while True:
            # 取得するテーブル・列・条件を指定し、execute()で問い合わせを実行する。
            # 実行結果全体がresponse、その中のdataが取得した行のリストになる。
            response = (
                supabase
                .table("knowledge")
                .select("id, report_date")
                .order("id")
                .range(start, start + 499)
                .execute()
            )
            # 今回の問い合わせで取得した行だけを取り出す。
            # rowsは各行を辞書にしたリスト。この後のfor文で1行ずつ処理する。
            rows = response.data or []
            if not rows:
                break

            for row in rows:
                # 報告日がある行だけ処理する。先頭4文字を年として整数に変換し、
                # まだyearsにない年だけ追加して、選択肢の重複を防ぐ。
                if row.get("report_date"):
                    year = int(row["report_date"][:4])
                    if year not in years:
                        years.append(year)
            start += len(rows)
    except Exception:
        raise RuntimeError("報告年を取得できませんでした。") from None

    # 大きい年から順に並べる。例：[2025, 2026]を[2026, 2025]へ。
    years.sort(reverse=True)
    return years


def list_knowledge(
    category_id=None, year=None, result_id=None
) -> list[dict]:
    """カテゴリ・報告年・結果に合う事例を取得する。省略した条件は絞り込まない"""
    supabase = get_client() # 接続用の関数を呼び出し
    records = []            # 複数回に分けて取得する全事例を、このリストへ順番に蓄積する。
    start = 0               # 何行目から取得するかを表す開始位置。最初は0行目から取得する。
    try:
        # 1回の取得上限(500回)を超える場合に備えて、取得を繰り返す。
        # 下の「if not rows」でデータが尽きたことを確認し、breakで終了する。
        while True:
            # ER図の外部キーを使い、名称・キーワードも一緒に取得する
            # ここでは問い合わせの条件を組み立てる。実行は後のexecute()で行う。
            # select内のusers(name)等は、外部キーでつながる表の名称も取得する指定。
            query = (
                supabase
                .table("knowledge")
                .select(
                    "id, user_id, product_category_id, result_id, report_date,"
                    "customer_attribute, customer_needs, proposal, reflection, created_at,"
                    "users(name), product_category(name), result(name),"
                    "knowledge_keyword(keyword(name))"
                )
            )
            # カテゴリを選んだときだけ一致条件を追加する。
            # Noneは「すべて」の意味なので、その場合はカテゴリで絞らない。
            if category_id is not None:
                query = query.eq("product_category_id", category_id)
            # 年を選んだときは1月1日〜12月31日の範囲を条件に加える。
            # gteは以上、lteは以下。比較対象は登録日時ではなく報告日。
            # 【追加】接客結果で絞り込む。Noneなら絞り込まない。
            if result_id is not None:
                query = query.eq("result_id", result_id)
            if year is not None:
                query = query.gte("report_date", f"{int(year):04d}-01-01")
                query = query.lte("report_date", f"{int(year):04d}-12-31")

            # 取得するテーブル・列・条件を指定し、execute()で問い合わせを実行する。
            # 実行結果全体がresponse、その中のdataが取得した行のリストになる。
            response = (
                query
                .order("id")
                .range(start, start + 499)
                .execute()
            )
            # 今回の問い合わせで取得した行だけを取り出す。
            # rowsは各行を辞書にしたリスト。この後のfor文で1行ずつ処理する。
            rows = response.data or []
            if not rows:
                break

            for row in rows:
                # 取得した1行の辞書をコピーし、画面・検索向けの項目を追加する。
                # 元のrowへ直接名前やkeywordsを書き足さないようにしている。
                record = row.copy()
                # 関連表の情報は辞書の中に入っているため、まず取り出す。
                # 関連データがNoneなら{}を使い、次のget("name")でエラーにしない。
                user = row.get("users") or {}
                category = row.get("product_category") or {}
                result = row.get("result") or {}
                record["user_name"] = user.get("name", "")
                record["category_name"] = category.get("name", "")
                record["result_name"] = result.get("name", "")

                keywords = []
                # 中間テーブルの各紐付けからkeywordのnameを取り出す。
                # 空の名前や重複は入れず、["省エネ", "電気代"]のようなリストにする。
                for link in row.get("knowledge_keyword") or []:
                    keyword = link.get("keyword") or {}
                    name = keyword.get("name")
                    if name and name not in keywords:
                        keywords.append(name)
                # 整えたキーワードを事例の辞書へ付け、この事例を全件用リストへ追加する。
                record["keywords"] = keywords
                records.append(record)

            # 取得上限で途中の事例を見落とさないよう、次の範囲へ進む。
            # 実際の取得件数で進めるので、DB側の上限が500件未満でも対応。
            start += len(rows)
    except Exception:
        # 0件と通信・権限エラーを区別するため、失敗時に[]は返さない。
        raise RuntimeError(
            "事例を取得できませんでした。通信状態を確認してください。管理者は外部キー、SELECT権限・RLSを確認してください。"
        ) from None

    # 取得と整形が終わった全事例を返す。ここでは順位付けはまだ行わない。
    return records

def create_knowledge(data: dict, keywords: list[str]) -> str:
    """事例を1件登録し、キーワードを紐付けて、登録した事例の id を返す。"""
    supabase = get_client()
    try:
        # ① 事例を登録する。ID は画面側で変換済みのものを受け取る
        response = (
            supabase
            .table("knowledge")
            .insert({
                "user_id": data["user_id"],
                "product_category_id": data["product_category_id"],
                "result_id": data["result_id"],
                "report_date": data["report_date"],
                "customer_attribute": data.get("customer_attribute") or "",
                "customer_needs": data.get("customer_needs") or "",
                "proposal": data.get("proposal") or "",
                "reflection": data.get("reflection") or "",
            })
            .execute()
        )
        knowledge_id = response.data[0]["id"]

        # ② キーワードを keyword に追加し（すでにあれば何もしない）、③ 事例と紐付ける
        names = []
        for keyword in keywords:
            if keyword and keyword.strip() and keyword.strip() not in names:
                names.append(keyword.strip())
        for name in names:
            keyword_response = (
                supabase
                .table("keyword")
                .upsert({"name": name}, on_conflict="name")
                .execute()
            )
            supabase.table("knowledge_keyword").upsert({
                "knowledge_id": knowledge_id,
                "keyword_id": keyword_response.data[0]["id"],
            }).execute()

        return knowledge_id
    except Exception:
        raise RuntimeError("事例を登録できませんでした。通信状態を確認してください。") from None