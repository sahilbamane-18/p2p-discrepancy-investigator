import csv
from pathlib import Path

from models import DeliveryRecord, InvoiceRecord, PurchaseOrderLine


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def load_purchase_orders(path: str | Path):
    path = Path(path)
    records = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            records.append(
                PurchaseOrderLine(
                    vendor_id=(row.get("vendor_id") or "").strip(),
                    po_number=(row.get("po_number") or "").strip(),
                    item_code=(row.get("item_code") or "").strip(),
                    quantity=_to_float(row.get("quantity")),
                    unit_price=_to_float(row.get("unit_price")),
                    currency=(row.get("currency") or "USD").strip() or "USD",
                )
            )
    return records


def load_deliveries(path: str | Path):
    path = Path(path)
    records = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            records.append(
                DeliveryRecord(
                    vendor_id=(row.get("vendor_id") or "").strip(),
                    po_number=(row.get("po_number") or "").strip(),
                    item_code=(row.get("item_code") or "").strip(),
                    quantity=_to_float(row.get("quantity")),
                    delivery_id=(row.get("delivery_id") or "").strip(),
                )
            )
    return records


def load_invoices(path: str | Path):
    path = Path(path)
    records = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            records.append(
                InvoiceRecord(
                    vendor_id=(row.get("vendor_id") or "").strip(),
                    po_number=(row.get("po_number") or "").strip(),
                    invoice_number=(row.get("invoice_number") or "").strip(),
                    item_code=(row.get("item_code") or "").strip(),
                    quantity=_to_float(row.get("quantity")),
                    unit_price=_to_float(row.get("unit_price")),
                )
            )
    return records
