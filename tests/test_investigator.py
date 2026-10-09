# Test fixture for Duplicate invoice detection and discrepancy scoring

from app.investigator import DiscrepancyInvestigator


def build_sample_records():
    purchase_orders = [
        {
            "vendor_id": "VEND-001",
            "po_number": "PO-1001",
            "item_code": "MOUSE",
            "quantity": 100,
            "unit_price": 25.0,
        },
        {
            "vendor_id": "VEND-001",
            "po_number": "PO-1001",
            "item_code": "KEYBOARD",
            "quantity": 40,
            "unit_price": 45.0,
        },
        {
            "vendor_id": "VEND-002",
            "po_number": "PO-2102",
            "item_code": "MONITOR",
            "quantity": 20,
            "unit_price": 180.0,
        },
        {
            "vendor_id": "VEND-003",
            "po_number": "PO-3303",
            "item_code": "LAPTOP",
            "quantity": 5,
            "unit_price": 980.0,
        },
    ]

    deliveries = [
        {
            "vendor_id": "VEND-001",
            "po_number": "PO-1001",
            "item_code": "MOUSE",
            "quantity": 100,
            "delivery_id": "D-001",
        },
        {
            "vendor_id": "VEND-001",
            "po_number": "PO-1001",
            "item_code": "KEYBOARD",
            "quantity": 38,
            "delivery_id": "D-002",
        },
        {
            "vendor_id": "VEND-002",
            "po_number": "PO-2102",
            "item_code": "MONITOR",
            "quantity": 18,
            "delivery_id": "D-003",
        },
        {
            "vendor_id": "VEND-003",
            "po_number": "PO-3303",
            "item_code": "LAPTOP",
            "quantity": 5,
            "delivery_id": "D-004",
        },
    ]

    invoices = [
        {
            "vendor_id": "VEND-001",
            "po_number": "PO-1001",
            "invoice_number": "INV-1001",
            "item_code": "MOUSE",
            "quantity": 90,
            "unit_price": 25.0,
        },
        {
            "vendor_id": "VEND-001",
            "po_number": "PO-1001",
            "invoice_number": "INV-1002",
            "item_code": "KEYBOARD",
            "quantity": 42,
            "unit_price": 50.0,
        },
        {
            "vendor_id": "VEND-002",
            "po_number": "PO-2102",
            "invoice_number": "INV-2001",
            "item_code": "MONITOR",
            "quantity": 25,
            "unit_price": 180.0,
        },
        {
            "vendor_id": "VEND-003",
            "po_number": "PO-3303",
            "invoice_number": "INV-3001",
            "item_code": "LAPTOP",
            "quantity": 5,
            "unit_price": 980.0,
        },
        {
            "vendor_id": "VEND-001",
            "po_number": "PO-1001",
            "invoice_number": "INV-1001",
            "item_code": "MOUSE",
            "quantity": 90,
            "unit_price": 25.0,
        },
    ]

    return purchase_orders, deliveries, invoices


def test_investigator_identifies_discrepancies():
    purchase_orders, deliveries, invoices = build_sample_records()
    investigator = DiscrepancyInvestigator(purchase_orders, deliveries, invoices)
    report = investigator.investigate()

    assert report["summary"]["case_count"] >= 3
    assert report["summary"]["duplicate_invoice_groups"] >= 1
    assert any(case["invoice_number"] == "INV-1001" for case in report["cases"])
    assert any(case["invoice_number"] == "INV-1002" for case in report["cases"])
