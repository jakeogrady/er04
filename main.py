from pathlib import Path
from tempfile import mkdtemp

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.readers.docling import DoclingReader
from llama_index.vector_stores.milvus import MilvusVectorStore


def main():
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    model_id = "Qwen/Qwen2.5-1.5B-Instruct"

    llm = HuggingFaceLLM(
        model_name=model_id,
        tokenizer_name=model_id,
        model_kwargs={"trust_remote_code": True},
        tokenizer_kwargs={"trust_remote_code": True},
    )

    source = "../bitcoin.pdf"
    query = """I want you to write flashcards based off of the information in this document. It should be written in json like so:
             [
                'question_1': {
                            'front': '<>',
                            'back': '<>',
                },
                'question_2': {
                        'front': '<>',
                        'back': '<>',
                }
            ]
            
            Write 10 of these questions in this format.
             """

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
    result = index.as_query_engine(llm=llm).query(query)

    print(f"Q: {query}\nA: {result.response.strip()}")


if __name__ == "__main__":
    main()
