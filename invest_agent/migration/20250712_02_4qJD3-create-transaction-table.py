"""
Create Transaction table
"""

from yoyo import step

__depends__ = {"20250712_01_oND4u-create-order-table"}

steps = [
    step(
        """
        CREATE TABLE transactions (
            id TEXT PRIMARY KEY,
            sell_balance JSON NOT NULL,
            buy_balance JSON NOT NULL,
            type TEXT CHECK(type IN ('SELL', 'BUY', 'SWAP')) NOT NULL,
            created_at INTEGER NOT NULL,
            transaction_hash TEXT NOT NULL,
            order_id TEXT,
            trigger TEXT CHECK(trigger IN ('MANUAL', 'AUTOMATIC')) NOT NULL,
            fees JSON,
            basket_id TEXT
        );
        """,
        "DROP TABLE transactions",
    ),
    step(
        """
        CREATE UNIQUE INDEX idx_transactions_order_id_unique
        ON transactions (order_id);
        """,
        "DROP INDEX idx_transactions_order_id_unique",
    ),
]
