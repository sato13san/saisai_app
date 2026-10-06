# services/check.py
"""入力内容のチェック。カテゴリと内容が食い違っていないかを、言葉の辞書で確かめる"""

#カテゴリごとの「らしい言葉」。カテゴリを増やしたらここに追加する
category_words = {
    "エアコン": ["エアコン", "冷房", "暖房", "空調", "室温"],
    "冷蔵庫": ["冷蔵庫", "冷凍庫", "冷凍", "冷蔵", "氷"],
    "洗濯機": ["洗濯機", "乾燥機", "ドラム式", "縦型", "洗濯", "乾燥"],
}

def find_other_categories(selected: str, text: str) -> list[str]:
    """選んだカテゴリの言葉が無く、他のカテゴリの言葉がある場合に、そのカテゴリ名を返す。"""
    if selected not in category_words:
        return []
    if any(word in text for word in category_words[selected]):
        return [] # 選んだカテゴリの話もしているので問題なし
    return[
        category for category, words in category_words.items()
        if category != selected and any(word in text for word in words)
    ]