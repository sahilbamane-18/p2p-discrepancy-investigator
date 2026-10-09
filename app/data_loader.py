import csv
from pathlib import Path

from app.models import DeliveryRecord, InvoiceRecord, PurchaseOrderLine


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def load_purchase_orders(path: str | Path):
    records = []
    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            records.append(
                PurchaseOrderLine(
                    vendor_id=row["vendor_id"].strip(),
                    po_number=row["po_number"].strip(),
                    item_code=row["item_code"].strip(),
                    quantity=_to_float(row.get("quantity")),
                    unit_price=_to_float(row.get("unit_price")),
                    currency=row.get("currency", "USD").strip() or "USD",
                )
            )
    return records


def load_deliveries(path: str | Path):
    records = []
    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            records.append(
                DeliveryRecord(
                    vendor_id=row["vendor_id"].strip(),
                    po_number=row["po_number"].strip(),
                    item_code=row["item_code"].strip(),
                    quantity=_to_float(row.get("quantity")),
                    delivery_id=row.get("delivery_id", "").strip(),
                )
            )
    return records


def load_invoices(path: str | Path):
    records = []
    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            records.append(
                InvoiceRecord(
                    vendor_id=row["vendor_id"].strip(),
                    po_number=row["po_number"].strip(),
                    invoice_number=row["invoice_number"].strip(),
                    item_code=row["item_code"].strip(),
                    quantity=_to_float(row.get("quantity")),
                    unit_price=_to_float(row.get("unit_price")),
                )
            )
    return records
