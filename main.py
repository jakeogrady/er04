from pathlib import Path
from tempfile import mkdtemp

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.readers.docling import DoclingReader
from llama_index.vector_stores.milvus import MilvusVectorStore

from models import AnkiDeck
from note_generator import package_anki_deck
from query import QUERY


def main():
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    model_id = "Qwen/Qwen2.5-1.5B-Instruct"

    llm = HuggingFaceLLM(
        model_name=model_id,
        tokenizer_name=model_id,
        model_kwargs={"trust_remote_code": True},
        tokenizer_kwargs={"trust_remote_code": True},
    )

    sllm = llm.as_structured_llm(AnkiDeck)

    source = "../bitcoin.pdf"

    embed_dim = len(embed_model.get_text_embedding("hi"))

    reader = DoclingReader()
    node_parser = MarkdownNodeParser()

    vector_store = MilvusVectorStore(
        uri=str(Path(mkdtemp()) / "docling.db"),
        dim=embed_dim,
        overwrite=True,
    )
    index = VectorStoreIndex.from_documents(
        documents=reader.load_data(source),
        transformations=[node_parser],
        storage_context=StorageContext.from_defaults(vector_store=vector_store),
        embed_model=embed_model,
    )

    result = index.as_query_engine(llm=sllm).query(QUERY)

    print(f"{type(result)} = {result}")
    anki_deck = AnkiDeck.model_validate(result.response)
    print(anki_deck)
    package_anki_deck(anki_deck)


if __name__ == "__main__":
    main()
