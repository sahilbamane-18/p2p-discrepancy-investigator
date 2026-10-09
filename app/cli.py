import argparse
import json
from pathlib import Path

from app.data_loader import load_deliveries, load_invoices, load_purchase_orders
from app.investigator import DiscrepancyInvestigator


def build_investigator(data_dir: str | Path):
    data_dir = Path(data_dir)
    purchase_orders = load_purchase_orders(data_dir / "purchase_orders.csv")
    deliveries = load_deliveries(data_dir / "deliveries.csv")
    invoices = load_invoices(data_dir / "invoices.csv")
    return DiscrepancyInvestigator(purchase_orders, deliveries, invoices)


def print_report(report):
    summary = report["summary"]
    print("Purchase-to-Payment Discrepancy Investigation")
    print("=" * 52)
    print(f"Cases identified: {summary['case_count']}")
    print(f"Total financial impact: ${summary['total_financial_impact']:.2f}")
    print(f"Duplicate invoice groups: {summary['duplicate_invoice_groups']}")
    print(
        "Priority mix: "
        f"Critical={summary['priority_breakdown']['Critical']}, "
        f"High={summary['priority_breakdown']['High']}, "
        f"Medium={summary['priority_breakdown']['Medium']}, "
        f"Low={summary['priority_breakdown']['Low']}"
    )
    print()

    for case in report["cases"]:
        print(
            f"[{case['priority']}] {case['vendor_id']} | {case['po_number']} | "
            f"{case['invoice_number']} | {case['item_code']} | "
            f"Risk {case['risk_score']} | Impact ${case['financial_impact']:.2f}"
        )
        print(f"  Quantity delta: {case['quantity_delta']:+.2f} units")
        print(f"  Price delta: ${case['price_delta']:+.2f} per unit")
        print(f"  Reasons: {', '.join(case['reasons'])}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Purchase-to-Payment Discrepancy Investigator")
    parser.add_argument("--data-dir", default="data", help="Directory containing purchase_orders.csv, deliveries.csv, and invoices.csv")
    parser.add_argument("--json", action="store_true", help="Print the result as JSON instead of a terminal report")
    args = parser.parse_args()

    investigator = build_investigator(args.data_dir)
    report = investigator.investigate()

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    return 0
