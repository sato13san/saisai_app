"""類似事例提示（No.3）。入力中の接客事例に近い過去事例を、最大3件返す。"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from services.database import get_categories, list_knowledge

# この値より似ていない事例は出さない（要件：十分な類似事例がなければ無理に3件表示しない）
# todo: 実データで試しながら調整する
MIN_SCORE = 0.05


def _to_text(record: dict) -> str:
    """類似度を測るための文章を作る。顧客ニーズとキーワードを重めにする。"""
    keywords = " ".join(record.get("keywords") or [])
    needs = record.get("customer_needs") or ""
    proposal = record.get("proposal") or ""
    attribute = record.get("customer_attribute") or ""
    # ranking.py と同じく、重要な項目は繰り返して重みを付ける
    return " ".join([keywords] * 2 + [needs] * 2 + [proposal, attribute])


def _category_id(category_name: str):
    """「冷蔵庫」などのカテゴリ名を、DB の ID に変換する。見つからなければ None。"""
    for category in get_categories():
        if category["name"] == category_name:
            return category["id"]
    return None


def _to_title_detail(record: dict) -> dict:
    """画面表示用に title と detail の形へ整える。"""
    title = (
        f"【{record.get('result_name', '')}】{record.get('category_name', '')}｜"
        f"{record.get('customer_attribute', '')}（{record.get('report_date', '')}）"
    )
    detail = "  \n".join([
        f"**顧客ニーズ：** {record.get('customer_needs', '')}",
        f"**提案内容：** {record.get('proposal', '')}",
        f"**振り返り：** {record.get('reflection', '')}",
        f"**キーワード：** {'、'.join(record.get('keywords') or [])}",
    ])
    return {"title": title, "detail": detail}


def find_similar(case: dict, top_k: int = 3) -> list[dict]:
    """入力中の事例（case）に近い過去事例を、似ている順に最大 top_k 件返す。

    Args:
        case: 登録画面の入力内容。category（カテゴリ名）、customer_attribute、
            customer_needs、proposal を使う。keywords があれば加味する。
    Returns:
        [{"title": ..., "detail": ...}, ...]。似た事例がなければ []。
    """
    # 同じ商品カテゴリの事例だけを候補にする
    category_id = _category_id(case.get("category", ""))
    if category_id is None:
        return []
    records = list_knowledge(category_id=category_id)

    # 今登録したばかりの事例自身は候補から外す
    records = [
        r for r in records
        if not (r.get("customer_needs") == case.get("customer_needs")
                and r.get("proposal") == case.get("proposal"))
    ]
    query = _to_text(case)
    if not records or not query.strip():
        return []

    # 文字の並び（2〜3文字）で文章を数値化し、入力との近さを測る（ranking.py と同じ考え方）
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 3), sublinear_tf=True)
    matrix = vectorizer.fit_transform([_to_text(r) for r in records])
    scores = cosine_similarity(vectorizer.transform([query]), matrix)[0]

    # 似ている順に並べ、基準に届かない事例は出さない
    ranked = sorted(zip(scores, records), key=lambda x: x[0], reverse=True)
    return [_to_title_detail(r) for score, r in ranked[:top_k] if score >= MIN_SCORE]
