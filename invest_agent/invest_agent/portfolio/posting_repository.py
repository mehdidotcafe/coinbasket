from abc import ABC, abstractmethod

from invest_agent.portfolio.posting import Posting


class PostingRepository(ABC):
    @abstractmethod
    async def create_posting(self, posting: Posting) -> Posting:
        """Save an posting to the repository."""
        raise NotImplementedError
