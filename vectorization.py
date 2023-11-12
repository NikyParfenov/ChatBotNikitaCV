from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import os
import pandas as pd


def doc_vectorization(token, dir='docs', file='Content.xlsx'):
    embeddings = OpenAIEmbeddings(openai_api_key=token)
    try:
        docsearch = FAISS.load_local(os.path.join(dir, "db_faiss_index"), embeddings)
    except RuntimeError:
        df = pd.read_excel(os.path.join(dir, file))
        docs = []
        for line in range(len(df)):
            document = Document(page_content='; '.join([df.iloc[line, 0], df.iloc[line, 1]]),
                                metadata={
                                    'section': df.iloc[line, 0],
                                    'question': df.iloc[line, 1],
                                    'doc_content': df.iloc[line, 2],
                                          },
                                )
            docs.append(document)
        docsearch = FAISS.from_documents(docs, embeddings)
        docsearch.save_local(os.path.join(dir, "db_faiss_index"))
    return docsearch
