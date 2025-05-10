from uagents import Model


class SimilarityQuery(Model):
    query: str
    agent_key: str


class SimilarityValidResponse(Model):
    serialized: str
    retrieved_docs: str


class SimilarityResponse(Model):
    data: SimilarityValidResponse | str
