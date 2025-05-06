from data_agent.similarity.similarity_storage.similarity_storage import (
    SimilarityStorage,
)


class GetSimilaritiesUseCase:
    def __init__(self, storage: SimilarityStorage):
        self.storage = storage

    def execute(self, query: str):
        retrieved_docs = self.storage.similarity_search(query)
        serialized = "\n\n".join(
            (f"Source: {doc.metadata}\nContent: {doc.page_content}")
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs
