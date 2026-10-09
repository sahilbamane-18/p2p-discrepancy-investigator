import argparse
import json
from pathlib import Path

from app.config import ToleranceConfig
from app.data_loader import load_deliveries, load_invoices, load_purchase_orders
from app.investigator import DiscrepancyInvestigator
from app.store import ReviewQueueStore


def build_investigator(data_dir: str | Path, tolerance=None):
    data_dir = Path(data_dir)
    purchase_orders = load_purchase_orders(data_dir / "purchase_orders.csv")
    deliveries = load_deliveries(data_dir / "deliveries.csv")
    invoices = load_invoices(data_dir / "invoices.csv")
    return DiscrepancyInvestigator(purchase_orders, deliveries, invoices, tolerance=tolerance)


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
            f"{case['case_type']} | Risk {case['risk_score']} | Impact ${case['financial_impact']:.2f}"
        )
        print(f"  Quantity delta: {case['quantity_delta']:+.2f} units")
        print(f"  Price delta: ${case['price_delta']:+.2f} per unit")
        print(f"  Reasons: {', '.join(case['reasons'])}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Purchase-to-Payment Discrepancy Investigator")
    parser.add_argument("--data-dir", default="data", help="Directory containing purchase_orders.csv, deliveries.csv, and invoices.csv")
    parser.add_argument("--json", action="store_true", help="Print the result as JSON instead of a terminal report")
    parser.add_argument("--export-json", help="Optional path to export the report as JSON")
    parser.add_argument("--save-db", action="store_true", help="Persist review queue cases to SQLite")
    parser.add_argument("--quantity-tolerance-pct", type=float, default=0.02, help="Allowed quantity variance above expected value")
    parser.add_argument("--price-tolerance-pct", type=float, default=0.02, help="Allowed price variance above expected value")
    args = parser.parse_args()

    tolerance = ToleranceConfig(
        quantity_tolerance_pct=args.quantity_tolerance_pct,
        price_tolerance_pct=args.price_tolerance_pct,
        quantity_absolute_tolerance=0.0,
        price_absolute_tolerance=0.0,
    )

    investigator = build_investigator(args.data_dir, tolerance=tolerance)
    report = investigator.investigate()

    if args.save_db:
        store = ReviewQueueStore("data/review_queue.db")
        store.save_cases(report["cases"])
        print("Saved review queue to data/review_queue.db")

    if args.export_json:
        output_path = Path(args.export_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Report exported to {output_path}")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    return 0
