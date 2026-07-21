#!/usr/bin/env python3
"""
RAG QA Bot — Query your knowledge base with LLMs.
Supports: Chroma, FAISS, Qdrant, Pinecone
"""

import os
import sys
import argparse
from pathlib import Path

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

try:
    from langchain_ollama import OllamaEmbeddings, ChatOllama
    from langchain_community.vectorstores import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import (
        TextLoader, PDFPlumberLoader, DirectoryLoader, UnstructuredMarkdownLoader
    )
except ImportError:
    print("⚠️  Install: pip install langchain langchain-community langchain-ollama chromadb")
    sys.exit(1)


DEFAULT_COLLECTION = "agent-studio-kb"
DEFAULT_MODEL = "llama3.2"
DEFAULT_EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64


class RAGBot:
    def __init__(
        self,
        persist_dir: str = "./chroma_db",
        collection: str = DEFAULT_COLLECTION,
        embedding_model: str = DEFAULT_EMBED_MODEL,
        llm_model: str = DEFAULT_MODEL,
        vector_store: str = "chroma"
    ):
        self.persist_dir = persist_dir
        self.collection = collection
        self.vector_store = vector_store

        self.embeddings = OllamaEmbeddings(model=embedding_model)
        self.llm = ChatOllama(model=llm_model, temperature=0.3)

        if vector_store == "chroma":
            self.vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embeddings,
                collection_name=collection
            )

    def index_folder(self, folder_path: str, file_types: list = None):
        """Index all documents from a folder."""
        if file_types is None:
            file_types = ["*.md", "*.txt", "*.pdf"]

        docs = []
        for ft in file_types:
            loader = DirectoryLoader(folder_path, glob=ft, loader_cls=TextLoader)
            docs.extend(loader.load())

        print(f"📄 Loaded {len(docs)} documents")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        chunks = splitter.split_documents(docs)
        print(f"✂️  Split into {len(chunks)} chunks")

        self.vectorstore.add_documents(chunks)
        print(f"✅ Indexed {len(chunks)} chunks to '{self.collection}'")

    def ask(self, query: str, top_k: int = 5) -> str:
        """Ask a question — returns LLM-generated answer."""
        docs = self.vectorstore.similarity_search(query, k=top_k)
        context = "\n\n".join([d.page_content for d in docs])

        prompt = f"""Answer based ONLY on the provided context.
If the answer is not in the context, say "I don't have that information."

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""

        response = self.llm.invoke(prompt)
        return response.content

    def search(self, query: str, top_k: int = 5) -> list:
        """Semantic search — returns raw context chunks."""
        return self.vectorstore.similarity_search(query, k=top_k)


def main():
    parser = argparse.ArgumentParser(description="RAG QA Bot")
    parser.add_argument("--folder", "-f", help="Folder to index")
    parser.add_argument("--query", "-q", help="Question to ask")
    parser.add_argument("--top-k", "-k", type=int, default=5, help="Top-k results")
    parser.add_argument("--collection", "-c", default=DEFAULT_COLLECTION)
    parser.add_argument("--persist-dir", "-p", default="./chroma_db")
    parser.add_argument("--llm", default=DEFAULT_MODEL)
    parser.add_argument("--embed", default=DEFAULT_EMBED_MODEL)

    args = parser.parse_args()

    bot = RAGBot(
        persist_dir=args.persist_dir,
        collection=args.collection,
        embedding_model=args.embed,
        llm_model=args.llm
    )

    if args.folder:
        print(f"📁 Indexing: {args.folder}")
        bot.index_folder(args.folder)

    if args.query:
        print(f"\n❓ Question: {args.query}")
        print(f"🔍 Searching (top_k={args.top_k})...")
        answer = bot.ask(args.query, top_k=args.top_k)
        print(f"\n💡 Answer:\n{answer}")


if __name__ == "__main__":
    main()
