from typing import TYPE_CHECKING, Any, Literal, Sequence, Tuple, cast
from decimal import Decimal
import json
from api.database.infrastructure.sql_alchemy_base import Base
from api.database.infrastructure.sql_alchemy_base_repository import (
    NullableSession,
    SqlAlchemyBaseRepository,
)

from api.portfolio.holding.holding import Holding
from api.portfolio.posting.posting import (
    Posting,
    PostingAssetType,
    PostingType,
)
from api.portfolio.posting.posting_repository import PostingRepository
from protocol.asset import Asset
from protocol.token import Token
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import ForeignKey, Row, String, or_, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import NUMERIC
from api.chain.balance import BalanceAtomic

if TYPE_CHECKING:
    from api.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
        TransactionModel,
    )


class PostingModel(Base):
    __tablename__ = "postings"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)

    asset_id: Mapped[str] = mapped_column(String())
    asset: Mapped[str] = mapped_column()
    amount: Mapped[str] = mapped_column()
    amount_atomic: Mapped[Decimal] = mapped_column(NUMERIC(78, 0))
    decimals: Mapped[int] = mapped_column()

    transaction_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("transactions.id")
    )
    created_at: Mapped[int] = mapped_column()
    type: Mapped[PostingType] = mapped_column()
    asset_type: Mapped[PostingAssetType] = mapped_column()
    basket_id: Mapped[str | None] = mapped_column(String(), nullable=True)

    transaction: Mapped["TransactionModel"] = relationship(
        "TransactionModel",
        back_populates="postings",
    )

    parent_posting_id: Mapped[str | None] = mapped_column(
        String(40),
        # No ForeignKey constraint because parent posting is created after child posting
        nullable=True,
    )

    def to_domain(self) -> Posting:
        return Posting(
            id=self.id,
            transaction_id=self.transaction_id,
            asset_balance=BalanceAtomic(
                asset=BalanceAtomic.deserialize_asset(self.asset),
                amount=Decimal(self.amount),
                amount_atomic=int(self.amount_atomic),
                decimals=self.decimals,
            ),
            type=self.type,
            created_at=self.created_at,
            basket_id=self.basket_id,
            parent_posting_id=self.parent_posting_id,
            asset_type=self.asset_type,
        )

    @staticmethod
    def from_domain(posting: Posting) -> "PostingModel":
        return PostingModel(
            id=posting.id,
            transaction_id=posting.transaction_id,
            asset_id=posting.asset_balance.asset.id,
            asset=json.dumps(posting.asset_balance.asset.to_dict()),
            amount=format(posting.asset_balance.amount, "f"),
            amount_atomic=posting.asset_balance.amount_atomic,
            decimals=posting.asset_balance.decimals,
            created_at=posting.created_at,
            type=posting.type,
            asset_type=posting.asset_type,
            basket_id=posting.basket_id,
            parent_posting_id=posting.parent_posting_id,
        )


class SqlAlchemyPostingRepository(PostingRepository, SqlAlchemyBaseRepository):
    def __init__(self, engine: AsyncEngine, AsyncSessionLocal: type[AsyncSession]):
        self.engine = engine
        self.AsyncSessionLocal = AsyncSessionLocal

    async def create_posting(
        self, posting: Posting, session: NullableSession = None
    ) -> Posting:
        async with self.get_session(session) as session:
            session.add(PostingModel.from_domain(posting))
        return posting

    async def get_holding_balances(
        self, session: NullableSession = None
    ) -> list[Holding]:
        async with self.get_session(session) as session:
            result = await session.execute(self._get_default_holding_statement())
            rows = result.all()

            return self._map_rows_to_holdings(rows)

    async def get_holding_balance(
        self, asset: Asset, asset_decimals: int, session: NullableSession = None
    ) -> Holding:
        async with self.get_session(session) as session:
            stmt = self._get_default_holding_statement().where(
                or_(
                    PostingModel.asset_id == asset.id,
                    PostingModel.basket_id == asset.id,
                )
            )
            result = await session.execute(stmt)
            rows = result.all()

            holdings = self._map_rows_to_holdings(rows)

            if not holdings:
                return Holding(
                    balance=BalanceAtomic.empty(asset=asset, decimals=asset_decimals),
                    children=[],
                )

            return holdings[0]

    def _get_default_holding_statement(self):
        return (
            select(
                PostingModel.asset_id,
                PostingModel.basket_id,
                func.min(PostingModel.asset_type),
                # Select any asset value of the same asset_id
                func.min(PostingModel.asset),
                func.min(PostingModel.decimals).label("decimals"),
                func.sum(PostingModel.amount_atomic).label("total_amount_atomic"),
            )
            .group_by(PostingModel.asset_id, PostingModel.basket_id)
            .order_by(PostingModel.asset_id.desc())
            .having(func.sum(PostingModel.amount_atomic) > 0)
        )

    # AI Generated
    def _map_rows_to_holdings(
        self,
        rows: Sequence[
            Row[Tuple[str, str | None, Literal["BASKET", "TOKEN"], str, int, Decimal]]
        ],
    ):
        # Parse rows into dicts for easier processing
        parsed: list[dict[str, Any]] = []
        for (
            asset_id,
            basket_id,
            asset_type,
            asset_json,
            decimals,
            total_amount_atomic,
        ) in rows:
            parsed.append(
                {
                    "asset_id": asset_id,
                    "basket_id": basket_id,
                    "asset_type": asset_type,
                    "asset_json": asset_json,
                    "decimals": decimals,
                    "total_amount_atomic": total_amount_atomic,
                }
            )

        # Build lookup for children: basket_id -> list of child rows
        children_by_basket: dict[str, list[dict[str, Any]]] = {}
        for row in parsed:
            if row["asset_type"] == "TOKEN" and row["basket_id"]:
                children_by_basket.setdefault(row["basket_id"], []).append(row)

        # Track asset_ids of all children to filter them out from top-level
        child_asset_ids: set[str] = set()
        for child_list in children_by_basket.values():
            for child in child_list:
                child_asset_ids.add(child["asset_id"])

        holdings: list[Holding] = []
        for row in parsed:
            # Only skip if this row is a child (TOKEN with basket_id) and is being included as a child in a basket
            if (
                row["asset_type"] == "TOKEN"
                and row["basket_id"]
                and row["asset_id"] in child_asset_ids
            ):
                continue  # skip child holdings that are included in a basket
            if row["asset_type"] == "BASKET":
                # Find children for this basket
                children_rows = children_by_basket.get(row["asset_id"], [])
                children = [self._map_row_to_balance(child) for child in children_rows]
                holding = Holding(
                    balance=self._map_row_to_balance(row),
                    children=cast(list[BalanceAtomic[Token]], children) or None,
                )
                holdings.append(holding)
            else:
                holding = Holding(
                    balance=self._map_row_to_balance(row),
                    children=None,
                )
                holdings.append(holding)
        return holdings

    def _map_row_to_balance(self, row: dict[str, Any]):
        return BalanceAtomic(
            asset=BalanceAtomic.deserialize_asset(row["asset_json"]),
            amount=row["total_amount_atomic"] / Decimal(10 ** row["decimals"]),
            amount_atomic=int(row["total_amount_atomic"]),
            decimals=row["decimals"],
        )
