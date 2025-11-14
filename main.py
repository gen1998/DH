import os
import streamlit as st
import faiss
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import numpy as np
from PIL import Image
from pathlib import Path
from src.utils import explain_search_word


def main():
    st.set_page_config(page_title="Radiology Search", layout="wide")
    st.title("🩻 Radiology Search")
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    report_index = faiss.read_index("./data/faiss/faiss_index.idx")
    df_report = pd.read_csv("./data/csv/report.csv")

    with st.sidebar:
        st.header("設定")
        top_k = st.slider("Top-K", 1, 20, 5)
    
    st.subheader("検索")
    researh_word = st.text_input("疾患など (MR/CT関連)", value="")
    btn = st.button("検索実行", type="primary")

    if btn and researh_word.strip():
        with st.spinner("検索中…"):
            res = client.embeddings.create(
                model="text-embedding-3-large",
                input=researh_word
            )
            query = np.array(res.data[0].embedding, dtype="float32").reshape(1, -1)
            distances, indices = report_index.search(query, top_k)

            query_meaning = explain_search_word(client, researh_word)     

        scores = distances[0]
        index = indices[0]

        st.success("完了")
        st.subheader("検索結果")
        st.markdown(f"**検索語の説明:** {query_meaning}")
        for rank, (idx, score) in enumerate(zip(index, scores), start=1):
            with st.container():
                st.markdown(f"### Rank {rank} (Score: {score:.4f})")
                col_img, col_text = st.columns([1.2, 2.0], gap="large")
                img_name = df_report.loc[idx, "image_name"]
                img_path = Path(f"./data/img/{img_name}")  # 症例に対応する.jpg
                img = Image.open(img_path)
                with col_img:
                    st.image(img, use_container_width=True)
                with col_text:
                    findings_jp = df_report.loc[idx, "findings_jp"]
                    impression_jp = df_report.loc[idx, "impression_jp"]
                    st.markdown("**診断(日本語)**")
                    st.write(impression_jp)
                    st.markdown("**所見(日本語)**")
                    st.write(findings_jp)
                st.markdown("---")


if __name__ == "__main__":
    main()
