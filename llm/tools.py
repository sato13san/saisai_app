import streamlit as st
from openai import OpenAI


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
以下の接客事例から、検索に役立つ重要なキーワードを抽出してください。

【ルール】
- 最大5個
- 短い言葉で表現する
- 顧客属性、顧客ニーズ、商品特徴、提案内容などを優先する
- 商品カテゴリと同じキーワードは入れない
- 販売結果と同じキーワードは入れない
- キーワードだけをカンマ区切りで出力する
- 説明文は不要

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
        )

        # AIの回答を取得
        output = response.output_text.strip()

        if not output:
            return []

        # カンマで分割してリスト化
        keywords = [
            keyword.strip()
            for keyword in output.split(",")
            if keyword.strip()
        ]

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