# Purchase-to-Payment Discrepancy Investigator

This project is a Python-based workflow for identifying financial mismatches between purchase orders (POs), delivery records, and supplier invoices. It is designed to help teams quickly isolate overpayments, duplicate billing, quantity discrepancies, and pricing problems before payment is released.

## What it does

- Imports purchase orders, deliveries, and invoices from CSV files
- Matches records by vendor, PO number, and item code
- Detects duplicate invoices
- Identifies quantity differences and unit price mismatches
- Calculates a financial discrepancy amount for each case
- Scores and prioritizes cases for review
- Prints a summary report and can export JSON

## Typical use cases

- Accounts payable review
- Procurement exception handling
- Supplier audit and compliance checks
- Overpayment prevention

## Project structure

- `app/` — core Python logic
- `data/` — sample P2P datasets
- `tests/` — validation tests
- `main.py` — entry point

## Quick start

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the investigator with sample data:
   ```bash
   python main.py
   ```

4. Export structured results as JSON:
   ```bash
   python main.py --json
   ```

## Sample output

The app produces a prioritized list such as:

- Critical: overpayment / duplicate supplier invoice
- High: quantity mismatch beyond tolerance
- Medium: minor price variance
- Low: informational variance within tolerance

## Example categories detected

- Duplicate invoice number for same supplier
- Invoice quantity exceeds PO or received quantity
- Invoice price differs from agreed contract price
- Unexpected item or unmatched invoice line
- Financial impact above threshold

## Extending the tool

You can extend this project by:

- adding database storage (SQLite/Postgres)
- importing Excel files
- adding tolerance configuration per supplier or item class
- creating a web dashboard with FastAPI or Streamlit
- exporting review queues to a business workflow tool

## License

MIT
