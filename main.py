import json
from pathlib import Path
from tempfile import mkdtemp

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.llms.ollama import Ollama
from llama_index.readers.docling import DoclingReader
from llama_index.vector_stores.milvus import MilvusVectorStore

from models import AnkiDeck
from note_generator import package_anki_deck
from query import SYSTEM_PROMPT, USER_PROMPT


def main():
    embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5", device="cpu"
    )

    llm = Ollama(
        model="llama3.2:3b", request_timeout=300, json_mode=True, context_window=2048
    )

    sllm = llm.as_structured_llm(AnkiDeck)

    embed_dim = len(embed_model.get_text_embedding("hi"))

    reader = DoclingReader()
    node_parser = MarkdownNodeParser()

    vector_store = MilvusVectorStore(
        uri=str(Path(mkdtemp()) / "docling.db"),
        dim=embed_dim,
        overwrite=True,
    )
    index = VectorStoreIndex.from_documents(
        documents=reader.load_data("../bitcoin.pdf"),
        transformations=[node_parser],
        storage_context=StorageContext.from_defaults(vector_store=vector_store),
        embed_model=embed_model,
    )

    # Get top nodes from the vector store
    query_engine = index.as_query_engine(llm=llm)  # raw LLM, not structured
    top_nodes = query_engine.retrieve(USER_PROMPT)  # pseudo-code

    # Combine text from nodes
    context_text = "\n\n".join(node.get_text() for node in top_nodes)

    # Pass the PDF content + prompt to the structured LLM
    result = sllm.complete(SYSTEM_PROMPT + "\n\n" + context_text)
    json_response = json.loads(result.text)
    anki_deck = AnkiDeck.model_validate(json_response)
    package_anki_deck(anki_deck)


if __name__ == "__main__":
    main()
