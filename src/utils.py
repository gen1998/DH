SYSTEM_PROMPT = """
あなたは放射線診断専門のアシスタントです。
入力される検索語は、MRやCTに関連する疾患名・所見名・検査目的などの単語または短い文章です。
これについて、放射線画像診断の観点から、非専門家にもわかる日本語で説明してください。

制約:
- 出力は必ず「日本語のプレーンテキスト」だけにする（Markdownや箇条書きは禁止）。
- 文字数は句読点を含めておおよそ100文字（目安: 90〜120文字）。
- MR/CT画像でどのような所見や役割があるかを中心に簡潔に説明する。
- 用語があいまいでも、一般的に最も自然な解釈で説明する。
"""

def explain_search_word(client, query: str) -> str:
    """単語/文章どちらでもOK。約100文字の日本語説明を返す。"""
    resp = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"検索語: {query}\n説明: "}
        ],
        temperature=0.3,                 # ぶれを抑える
        max_output_tokens=150,           # 文字ではなくトークン。100字前後なら十分
    )
    text = resp.output_text  # SDKが本文だけ取り出してくれる
    # 念のため120文字でトリム（文末を崩さない範囲）
    text = text.replace("\n", " ").strip()
    if len(text) > 120:
        text = text[:120].rstrip("、。・,.;：:!?！？」』 ") + "…"
    return text