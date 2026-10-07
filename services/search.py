from services.database import list_knowledge
from services.ranking import SearchEngine

def _make_preview(record: dict, length: int = 100) -> str:
    """宿題のプレビューを、今回の要件に合わせて本文先頭約100文字に変更。"""
    # 本文を構成する3項目を、ニーズ→提案→振り返りの順で取り出す。
    parts = [record.get(field) or "" for field in (
        "customer_needs", "proposal", "reflection"
    )]
    # 3項目をつなぎ、下位行や連続する空白を1つの空白へ整える。
    text = " ".join(" ".join(parts).split())
    return text[:length] + ("..." if len(text) > length else "")

def search_knowledge(
    query: str,
    category_id=None,
    year=None,
    limit=20,
    result_id=None,
) -> list[dict]:
    """検索語必須。複数語AND検索の上位最大20件を返す。結果も対象に追加。"""
    # 入力条件が検索可能かを先に確認する。
    if not query.strip() or limit <= 0:
        return []

    records = list_knowledge(
    category_id=category_id,
    year=year,
    result_id=result_id,  # 【追加】
    )
    # 今回の検索用エンジンを作り、対象事例を登録してから検索する。
    engine = SearchEngine()
    engine.build_index(records)
    results = engine.search(query, top_n=limit)
    for record in results:
        # 検索結果の各辞書へ、一覧画面で使う短い本文を追加する。
        record["preview"] = _make_preview(record)

    return results