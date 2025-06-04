
"""
* Author: Lahiru Menikdiwela
* Email: lahirumenik@gmail.com
___________________________________________________________
* Date: Sat May 06 2025

"""


import os
import openai
import chromadb
import traceback
# import faiss
# from langchain_community.docstore.in_memory import InMemoryDocstore
# from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma
from utils.compress import get_skeleton
from utils.chunk import SimpleFixedLengthChunker
from utils.utils import serialize_dict_to_json
from dotenv import load_dotenv
from utils import utils

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def build(name):
    documents = []
    result = {}
    id = 0
    ids = []
    chunker = SimpleFixedLengthChunker()
    for root, dir, files in os.walk(name):
        for file in files:
            full_name = root + "/" + file
            if utils.is_invalid_path(full_name):
                # print(full_name)
                continue
            try:
                with open(f"{root}/{file}", "r") as f:
                    content = f.read()
                chunks = chunker.chunk_file(code=content)
                if chunks:
                    chunk_ids = []
                    for chunk in chunks:
                        doc = Document(page_content=chunk, metadata={"filename": f"{root}/{file}"})
                        documents.append(doc)
                        id += 1
                        ids.append(str(id))
                        chunk_ids.append(str(id))
                    result[f"{root}/{file}"] = ":".join(chunk_ids)
                else:
                    raise ValueError("Empty chunks array in vc.py at line:56 ...")
                # sketch = get_skeleton(content, keep_constant = True, keep_indent=True, total_lines =30, prefix_lines=15,suffix_lines=10)
                # if sketch:
                #     # print(sketch)
                #     doc = Document(page_content= sketch, metadata = {"filename": f"{root}/{file}"})
                #     documents.append(doc)
                #     id += 1
                #     ids.append(str(id))
                # else:
                #     print(sketch)
            except Exception as e:
                print(f"[!] Not an error but the file '{root}/{file}' seems to be empty which leads to: {e}")
    
    result["max_id"] = id
    serialize_dict_to_json(result, f"{name}_file_ids.json")
    
    client = chromadb.PersistentClient(path='chroma_db')
    collection = client.get_or_create_collection(f"{name}_chroma_index")

    vector_store = Chroma(
        client=client,
        collection_name=f"{name}_chroma_index",
        embedding_function=embeddings,
    )

    try:
        batch_ids = []
        if len(documents) > client.get_max_batch_size():
            batch_size = 4000
        else:
            batch_size = len(documents)
        for i in range(0, len(documents), batch_size):
            batch_documents = documents[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            vector_store.add_documents(documents=batch_documents, ids=batch_ids)
    except Exception as e:
        traceback.print_exc()
                    
if __name__ == "__main__":
    build("django")