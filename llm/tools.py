import re

import streamlit as st
from openai import OpenAI

# 初期データ（data/seed.sql）でよく使っているキーワード。
# AI に同じ表記を優先して使わせ、検索・類似事例で一致しやすくする。
EXAMPLE_KEYWORDS = (
    "まとめ買い、冷凍室重視、予算確認、予算オーバー、省エネ、電気代提示、数値で説明、"
    "設置スペース、寸法確認、時短、乾燥機能、共働き、高齢者、操作の簡単さ、体験提案、"
    "ニーズ深掘り、選択肢絞り込み、熱中症対策、要望とのずれ"
)


def generate_keywords(
    case_text: str,
    category: str = "",
    result: str = "",
) -> list[str]:
    """
    接客事例から検索用キーワードを最大5個生成する。

    Args:
        case_text: 接客事例の本文
        category: 商品カテゴリ
        result: 販売結果

    Returns:
        キーワードのリスト
        失敗した場合は空リスト
    """

    try:
        client = OpenAI(
            api_key=st.secrets["OPENAI_API_KEY"]
        )

        prompt = f"""
あなたは家電量販店の接客ナレッジを整理するアシスタントです。
以下の接客事例に、あとで似た事例を検索するためのキーワードを付けてください。

【ルール】
- 3〜5個。1つは2〜8文字程度の短い言葉にする
- 「お客様が何に困っていたか（ニーズ）」と「接客で何をしたか・何が論点だったか」を表す言葉にする
- 接客事例に書かれている内容だけから選ぶ。書かれていないことは推測で足さない
- 年代・人数・金額・型番などの数字や、入力の言葉の丸写しは避ける（例：「40代夫婦」「600L」「予算20万」は×）
- 商品カテゴリ名と販売結果は入れない
- 次の既存キーワードの中に事例に当てはまるものがあれば、同じ表記で使う（当てはまらないものは使わない）：{EXAMPLE_KEYWORDS}
- キーワードだけを、半角カンマ区切りで1行で出力する。説明は不要

【商品カテゴリ】
{category}

【販売結果】
{result}

【接客事例】
{case_text}
"""

        response = client.responses.create(
            model="gpt-5-nano",
            input=prompt,
            # 考える量を少なめにして応答を速くする（標準では8〜10秒かかり、NF-02の10秒に近かった）
            reasoning={"effort": "low"},
        )

        # AIの回答を取得
        output = response.output_text.strip()

        if not output:
            return []

        # カンマ（全角・読点も含む）や改行で分割してリスト化
        keywords = []
        for keyword in re.split(r"[,、，\n]", output):
            keyword = keyword.strip()
            if keyword and keyword not in keywords:
                keywords.append(keyword)

        # カテゴリ・結果との重複を除外
        excluded = {
            category.strip(),
            result.strip(),
        }

        keywords = [
            keyword
            for keyword in keywords
            if keyword not in excluded
        ]

        # 最大5個
        return keywords[:5]

    except Exception:
        # AI接続などに失敗した場合
        return []