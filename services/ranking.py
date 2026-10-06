"""宿題のSearchEngineを接客ナレッジ用に変更。"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 宿題と同じ「文字列を繰り返す回数」
# todo: 重みはとりあえず実装してみて後で微調整
WEIGHTS = {
    "keywords": 3,
    "customer_needs": 3,
    "proposal": 2,
    "reflection": 1,
    "customer_attribute": 1,
}

class SearchEngine:
    """TF-IDFで検索結果を関連度順に並べる。"""

    def __init__(self):
        # 文章を数値へ変換するルールを準備する。まだ事例の学習はしない。
        # 日本語を文字のまとまりで扱うため、単語の分かち書き処理は不要。
        self.vectorizer = TfidfVectorizer(
            analyzer = "char_wb",  # 文字N-gram（日本語のまま扱えるようにする）
            ngram_range = (2, 3),  # 2~3文字のまとまり
            max_features = 5000,
            min_df = 1,
            max_df = 0.95,
            sublinear_tf = True  #TFの対数スケーリング
        )
        self.tfidf_matrix = None    # インデックス（後で構築）
        # todo: Supabaseのknowledgeテーブルから持ってくる必要あり？
        self.pages = []             # 元のページデータを保持
        self.is_fitted = False      # インデックスが構築済みかどうかのフラグ
        self.search_texts = []      # AND条件を確認するための、重みづけ前の本文

    def build_index(self, pages: list):
        """全ページのTF-IDFインデックスを構築する
        
        Args:
            pages: ページ情報の辞書リスト
        """
        # 再構築時に古い事例を残さない。
        self.pages = pages
        self.is_fitted = False
        self.tfidf_matrix = None
        self.search_texts = []
        if not pages:
            return

        # corpusには「1事例につき1つの検索用文章」を入れる。
        # has_textは、少なくとも1件に空白以外の文章があるかを記録する。
        corpus = []
        has_text = False
        for page in pages:
            # キーワードが未設定でも処理できるよう、空リストを初期値にする。
            # 宿題のようなカンマ区切り文字列も、次のifでリストへ変換する。
            keywords = page.get("keywords") or []
            if isinstance(keywords, str):
                keywords = keywords.split(",")

            # キーワードのリストを1つの文字列にし、残りの4項目も取り出す。
            # Noneがあると文字列の連結に失敗するため、未入力は空文字に置き換える。
            keyword_text = " ".join(keywords)
            needs = page.get("customer_needs") or ""
            proposal = page.get("proposal") or ""
            reflection = page.get("reflection") or ""
            attribute = page.get("customer_attribute") or ""

            # 複数語が本文・キーワード・顧客属性に分かれていても検索できる。
            search_text = " ".join([
                keyword_text, needs, proposal, reflection, attribute
            ]).lower()
            # この文章は「検索語をすべて含むか」の確認用として保存する。
            # corpusとは同じ事例順なので、後で同じindexを使って取り出せる。
            self.search_texts.append(search_text)
            if search_text.strip():
                has_text = True

            # 重要な項目の文字列を繰り返す（宿題と同じ）
            text = " ".join([
                (keyword_text + " ") * WEIGHTS["keywords"],
                (needs + " ") * WEIGHTS["customer_needs"],
                (proposal + " ") * WEIGHTS["proposal"],
                (reflection + " ") * WEIGHTS["reflection"],
                (attribute + " ") * WEIGHTS["customer_attribute"],
            ])
            # 空欄の項目が作る先頭・末尾の空白は除く。
            corpus.append(text.strip())

        # 全項目が空のデータしかない場合は、TF-IDFを計算しない。
        if not has_text:
            return
        # 全事例から特徴とIDFを学習し、同時に各事例を数値の行列へ変換する。
        # 行は事例、列は文字の特徴に対応する。完了後に準備済みフラグとたてる。
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        self.is_fitted = True

    def search(self, query: str, top_n: int = 20) -> list:
        # 準備前・空の検索語・表示件数が0以下の場合は、計算もせず空リストを返す。
        # strip()は前後の空白を除くため、スペースだけの入力もここで止まる。
        if not self.is_fitted or not query.strip() or top_n <= 0:
            return []

        # split()で半角・全角スペースを区切る。同じ語は1つにする。
        words = []
        for word in query.lower().split():
            if word not in words:
                words.append(word)

        # 検索語を数値化→コサイン類似度を計算（宿題と同じ流れ）
        # 検索語を、事例で学習済みのルールを使って数値へ変換する。
        # ここでfit_transformし直すと事例側と特徴の対応が変わるので、transformを使う
        query_vec = self.vectorizer.transform([" ".join(words)])
        # 検索語を各事例のベクトルがどれくらい近いかを計算する。
        # 検索文は1つなので、結果の先頭行[0]を取り出すと各事例のスコアになる。
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        results = []
        # indexは事例の位置、base_scoreはその事例の類似度
        # 同じ位置の元データとAND確認用の文章を、以下の処理で参照する。
        for index, base_score in enumerate(similarities):
            # AND検索からOR検索に変更
            # 最初は不一致と仮定し、含まれる語が1つでも見つかればTrueとする。
            matched = False
            for word in words:
                if word in self.search_texts[index]:
                    matched = True
                    break
            # OR条件を満たさなかった事例は追加せず、次の事例に進む。
            # continueはsearch関数全体の終了ではなく、このfor文の次の周回を意味する。
            if not matched:
                continue

            # 元の辞書をコピーしてスコア付け
            page = self.pages[index].copy()
            page["relevance_score"] = float(base_score) * 100
            results.append(page)

        # 同スコアなら報告日が新しい順、ID順で並べる
        results.sort(key=lambda x: str(x["id"]))
        results.sort(
            key=lambda x: (x["relevance_score"], x.get("report_date") or ""),
            reverse=True,
        )
        # 要求された件数と20の小さい方を上限にする。
        return results[:min(top_n, 20)]