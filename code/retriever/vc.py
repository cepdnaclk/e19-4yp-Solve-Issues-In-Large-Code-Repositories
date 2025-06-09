
"""
* Author: Lahiru Menikdiwela
* Email: lahirumenik@gmail.com
___________________________________________________________
* Date: Sat May 06 2025

"""


from langchain_openai import OpenAIEmbeddings
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from langchain_core.documents import Document
from utils.embed_skeleton import get_skeleton
from utils.utils import serialize_dict_to_json
import os
from utils import utils

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

def build(name):
    documents = []
    id = 0
    ids = []
    for root,dir, files in os.walk(name):
        for file in files:
            if file.endswith(".py"):
                full_name = root + "/" + file
                if utils.is_invalid_path(full_name):
                # print(full_name)
                    continue
                try:
                    with open(f"{root}/{file}", "r") as f:
                        content = f.read()
                    sketch = get_skeleton(content, keep_constant = False, keep_indent=True, total_lines =30, prefix_lines=15,suffix_lines=10)
                    if sketch:
                        # print(sketch)
                        doc = Document(page_content= sketch, metadata = {"filename": f"{root}/{file}"})
                        documents.append(doc)
                        id += 1
                        ids.append(id)
                    # else:
                    #     print(sketch)
                except Exception as e:
                    print(f"[!] Error adding file '{root}/{file}': {e}")
    result = {}
    for i in range(len(documents)):
        result[documents[i].metadata['filename']] = ids[i]
    serialize_dict_to_json(result, f"{name}_file_ids.json")
    vector_store.add_documents(documents=documents, ids=ids)
    vector_store.save_local(f"{name}_faiss_index")
                    
if __name__ == "__main__":
    build("django")

    