from typing import List
from langchain_core.documents import Document
import re

class SimpleFixedLengthChunker:
    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_file(self, code: str) -> List[str]:
        # Remove excessive whitespace and normalize to single newlines
        normalized_code = re.sub(r'\n\s*\n+', '\n', code.strip())

        chunks = []
        start = 0
        while start < len(normalized_code):
            end = start + self.chunk_size
            chunks.append(normalized_code[start:end])
            start += self.chunk_size - self.chunk_overlap

        return chunks
    
    def dechunk_docs(self, chunk_docs: List[Document]) -> str:
        file_content = chunk_docs[0].page_content
        del chunk_docs[0]
        for chunk_doc in chunk_docs:
            file_content += chunk_doc.page_content[self.chunk_overlap:]

        return file_content

if __name__ == "__main__":
    chunker = SimpleFixedLengthChunker(chunk_size=500, chunk_overlap=100)

    with open('../graph.py', 'r') as f:
        code = f.read()
        chunks = chunker.chunk_file(code)

    for i, chunk in enumerate(chunks):
        print(f"\n=== Chunk {i+1} ({len(chunk)} chars) ===")
        print(chunk)
        print(f"\n{'-'*40}")
