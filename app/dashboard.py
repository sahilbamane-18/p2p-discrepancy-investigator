import json
from pathlib import Path

import pandas as pd
import streamlit as st

from config import ToleranceConfig
from data_loader import load_deliveries, load_invoices, load_purchase_orders
from investigator import DiscrepancyInvestigator


DATA_PATH = Path(__file__).resolve().parent.parent / "data"


def _load_default_data():
    purchase_orders = load_purchase_orders(DATA_PATH / "purchase_orders.csv")
    deliveries = load_deliveries(DATA_PATH / "deliveries.csv")
    invoices = load_invoices(DATA_PATH / "invoices.csv")
    return purchase_orders, deliveries, invoices


def _parse_csv_upload(uploaded_file):
    if uploaded_file is None:
        return None
    return pd.read_csv(uploaded_file)


def _render_summary(report):
    summary = report["summary"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cases", summary["case_count"])
    col2.metric("Financial impact", f"${summary['total_financial_impact']:.2f}")
    col3.metric("Duplicate groups", summary["duplicate_invoice_groups"])
    col4.metric("Largest case", f"${summary['largest_case']:.2f}")

    st.subheader("Priority mix")
    prio_cols = st.columns(4)
    priority_labels = ["Critical", "High", "Medium", "Low"]
    for idx, label in enumerate(priority_labels):
        prio_cols[idx].metric(label, summary["priority_breakdown"][label])


def _render_case_table(report):
    df = pd.DataFrame(report["cases"])
    if df.empty:
        st.info("No discrepancy cases detected for the current data set.")
        return

    display_cols = [
        "priority",
        "risk_score",
        "case_type",
        "vendor_id",
        "po_number",
        "invoice_number",
        "item_code",
        "financial_impact",
        "quantity_delta",
        "price_delta",
        "reasons",
    ]
    st.dataframe(df[display_cols], use_container_width=True, hide_index=True)


def main():
    st.set_page_config(page_title="P2P Discrepancy Investigator", layout="wide")
    st.title("Purchase-to-Payment Discrepancy Investigator")
    st.caption("Review invoice exceptions, duplicate bills, quantity drift, and pricing mismatches before payment release.")

    with st.sidebar:
        st.header("Controls")
        qty_tolerance = st.slider("Quantity tolerance (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.1) / 100.0
        price_tolerance = st.slider("Price tolerance (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.1) / 100.0

        st.subheader("Upload data")
        po_upload = st.file_uploader("Purchase orders CSV", type=["csv"])
        delivery_upload = st.file_uploader("Deliveries CSV", type=["csv"])
        invoice_upload = st.file_uploader("Invoices CSV", type=["csv"])

        use_demo_data = st.checkbox("Use bundled sample data", value=True)

    if use_demo_data:
        purchase_orders, deliveries, invoices = _load_default_data()
    else:
        purchase_orders = []
        deliveries = []
        invoices = []

    if po_upload is not None:
        po_df = pd.read_csv(po_upload)
        purchase_orders = [
            {
                "vendor_id": row["vendor_id"],
                "po_number": row["po_number"],
                "item_code": row["item_code"],
                "quantity": float(row["quantity"]),
                "unit_price": float(row["unit_price"]),
            }
            for _, row in po_df.iterrows()
        ]

    if delivery_upload is not None:
        del_df = pd.read_csv(delivery_upload)
        deliveries = [
            {
                "vendor_id": row["vendor_id"],
                "po_number": row["po_number"],
                "item_code": row["item_code"],
                "quantity": float(row["quantity"]),
                "delivery_id": str(row.get("delivery_id", "")),
            }
            for _, row in del_df.iterrows()
        ]

    if invoice_upload is not None:
        inv_df = pd.read_csv(invoice_upload)
        invoices = [
            {
                "vendor_id": row["vendor_id"],
                "po_number": row["po_number"],
                "invoice_number": row["invoice_number"],
                "item_code": row["item_code"],
                "quantity": float(row["quantity"]),
                "unit_price": float(row["unit_price"]),
            }
            for _, row in inv_df.iterrows()
        ]

    if not purchase_orders and not deliveries and not invoices:
        st.warning("No input data loaded. Use the bundled sample data or upload your own CSV files.")
        return

    tolerance = ToleranceConfig(
        quantity_tolerance_pct=qty_tolerance,
        price_tolerance_pct=price_tolerance,
        quantity_absolute_tolerance=0.0,
        price_absolute_tolerance=0.0,
    )

    investigator = DiscrepancyInvestigator(purchase_orders, deliveries, invoices, tolerance=tolerance)
    report = investigator.investigate()

    _render_summary(report)

    tabs = st.tabs(["Priority Queue", "Duplicate Invoices", "Details", "JSON"])

    with tabs[0]:
        _render_case_table(report)

    with tabs[1]:
        dup_df = pd.DataFrame(report.get("duplicate_invoices", {}).items(), columns=["Key", "Invoice Numbers"])
        if dup_df.empty:
            st.info("No duplicate invoice groups detected.")
        else:
            st.dataframe(dup_df, use_container_width=True, hide_index=True)

    with tabs[2]:
        if report["cases"]:
            details_df = pd.DataFrame(report["cases"])
            details_df["reasons"] = details_df["reasons"].apply(lambda x: ", ".join(x))
            st.dataframe(details_df, use_container_width=True, hide_index=True)
        else:
            st.info("No discrepancy details available.")

    with tabs[3]:
        st.code(json.dumps(report, indent=2), language="json")


if __name__ == "__main__":
    main()
