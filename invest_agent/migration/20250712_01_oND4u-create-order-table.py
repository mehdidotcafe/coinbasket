"""
Create Order table.
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """
        CREATE TABLE orders (
            id TEXT PRIMARY KEY,
            sell_balance JSON NOT NULL,
            buy_balance JSON NOT NULL,
            type TEXT CHECK(type IN ('SELL', 'BUY', 'SWAP')) NOT NULL,
            created_at INTEGER NOT NULL,
            status TEXT CHECK(status IN ('PENDING', 'SUCCESS', 'FAIL')) NOT NULL,
            trigger TEXT CHECK(trigger IN ('MANUAL', 'AUTOMATIC')) NOT NULL,
            basket_id TEXT
        );
        """,
        "DROP TABLE orders",
    ),
    step(
        """
        CREATE TABLE order_tries (
            id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            provider TEXT NOT NULL,
            buy_balance JSON NOT NULL,
            fees JSON,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
        );
        """,
        "DROP TABLE order_tries",
    ),
    step(
        """
        CREATE TABLE order_try_chain_transactions (
            id TEXT PRIMARY KEY,
            try_id TEXT NOT NULL,
            order_id TEXT NOT NULL,
            type TEXT CHECK(type IN ('SIGN', 'SEND')) NOT NULL,
            data TEXT NOT NULL,
            hash TEXT NOT NULL,
            status TEXT CHECK(status IN ('PENDING', 'SUCCESS', 'FAIL')) NOT NULL,
            FOREIGN KEY (try_id) REFERENCES order_tries(id) ON DELETE CASCADE,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
        );
        """,
        "DROP TABLE order_try_chain_transactions",
    ),
]
