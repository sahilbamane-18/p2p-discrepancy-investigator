import json
import sqlite3
from pathlib import Path


class ReviewQueueStore:
    def __init__(self, db_path: str | Path = "data/review_queue.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _initialize(self):
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS review_cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vendor_id TEXT,
                    po_number TEXT,
                    invoice_number TEXT,
                    item_code TEXT,
                    expected_quantity REAL,
                    invoice_quantity REAL,
                    expected_unit_price REAL,
                    invoice_unit_price REAL,
                    quantity_delta REAL,
                    price_delta REAL,
                    financial_impact REAL,
                    reasons TEXT,
                    priority TEXT,
                    risk_score INTEGER,
                    case_type TEXT,
                    review_status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.commit()

    def save_cases(self, cases):
        with sqlite3.connect(self.db_path) as connection:
            for case in cases:
                connection.execute(
                    """
                    INSERT INTO review_cases (
                        vendor_id, po_number, invoice_number, item_code,
                        expected_quantity, invoice_quantity, expected_unit_price,
                        invoice_unit_price, quantity_delta, price_delta, financial_impact,
                        reasons, priority, risk_score, case_type, review_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        case.get("vendor_id"),
                        case.get("po_number"),
                        case.get("invoice_number"),
                        case.get("item_code"),
                        case.get("expected_quantity"),
                        case.get("invoice_quantity"),
                        case.get("expected_unit_price"),
                        case.get("invoice_unit_price"),
                        case.get("quantity_delta"),
                        case.get("price_delta"),
                        case.get("financial_impact"),
                        json.dumps(case.get("reasons", [])),
                        case.get("priority"),
                        case.get("risk_score"),
                        case.get("case_type", "invoice_mismatch"),
                        case.get("review_status", "new"),
                    ),
                )
            connection.commit()

    def list_cases(self):
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute(
                "SELECT * FROM review_cases ORDER BY risk_score DESC, created_at DESC"
            ).fetchall()
        return rows
