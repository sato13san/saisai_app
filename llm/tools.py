import re
import json

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

def extract_search_query(consultation:str) -> dict:
    """相談文から、検索に使うカテゴリと検索語を取り出す。失敗したら空の値を返す。"""
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.responses.create(
            model="gpt-5-nano",
            reasoning={"effort": "minimal"},
            input=f"""家電量販店の販売員の相談文から、社内の接客事例を検索するための情報を取り出してください。
- category：相談文に出てくる商品がエアコン・冷蔵庫・洗濯機のどれか。商品名や「冷凍」「冷房」「ドラム式」などの言葉から判断する。分からなければ空文字
- words：相談文の要点を表す語を2〜4個。1語は2〜6文字の短い言葉にし、相談文に出てくる言葉をなるべくそのまま使う（例：「ネット」「価格」「工事日程」）。「お客様」「提案」のような一般的すぎる語は入れない
- 次の言葉は、相談文の内容に当てはまる場合だけ同じ表記で使う。当てはまらない言葉は使わない：{EXAMPLE_KEYWORDS}

【相談文】
{consultation}""",
            text={"format": {
                "type": "json_schema", "name": "search_query", "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "enum": ["エアコン", "冷蔵庫", "洗濯機", ""]},
                        "words": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["category", "words"],
                    "additionalProperties": False,
                },
            }},
        )
        data = json.loads(response.output_text)
        return {"category": data["category"], "words": [w.strip() for w in data["words"] if w.strip()][:5]}
    except Exception:
        return {"category": "", "words": []}

def summarize_cases(consultation: str, cases: list[dict]) -> str:
    """見つかった社内事例だけをもとに、相談への要約を作る。失敗したら空文字を返す。"""
    if not cases:
        return ""
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        case_text = "\n".join(
            f"【事例{i}】 結果：{c.get('result_name', '')}/ニーズ: {c.get('customer_needs', '')}/"
            f"提案: {c.get('proposal', '')}"
            for i, c in enumerate(cases, 1)
        )
        response = client.responses.create(
            model="gpt-5-nano",
            reasoning={"effort": "low"},
            input=f"""あなたは家電量販店の若手販売員を支える先輩です。
            次の社内事例だけをもとに、相談への参考になるポイントを3〜4文でまとめてください。
            - 事例に書かれていないことは書かない。一般論や推測で足さない
            - 根拠にした事例を「（事例１）」のように示す
            - 「〜すべき」「〜が有効」のような指導・評価の言い方は使わず、「〜した事例があります（事例1）」の形で書く
            - 各事例の「結果」（成約・検討・失注）を必ず確認し、成約した事例と、失注・検討の事例を混ぜて書かない
            - 失注・検討の事例は「〜して失注した事例があります」のように、結果がわかる書き方にする
            - まとめの文では、事例に書かれていない行動や対策を書かない。成約した事例の行動だけを「〜した事例があります」と書く
            
            【相談】
            {consultation}
            【社内事例】
            {case_text} """,
        )
        return response.output_text.strip()
    except Exception:
        return ""