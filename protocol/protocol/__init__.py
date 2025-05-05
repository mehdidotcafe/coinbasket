from uagents import Model


class SimilarityQuery(Model):
    query: str


class SimilarityResponse(Model):
    serialized: str
    retrieved_docs: str
