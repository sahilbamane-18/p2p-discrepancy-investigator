from collections import defaultdict

from config import ToleranceConfig
from models import DiscrepancyCase


class DiscrepancyInvestigator:
    def __init__(self, purchase_orders, deliveries, invoices, tolerance=None):
        self.purchase_orders = list(purchase_orders)
        self.deliveries = list(deliveries)
        self.invoices = list(invoices)
        self.tolerance = tolerance or ToleranceConfig()

    def _po_lookup(self):
        lookup = defaultdict(list)
        for order in self.purchase_orders:
            lookup[order.match_key()].append(order)
        return lookup

    def _delivery_lookup(self):
        lookup = defaultdict(float)
        for delivery in self.deliveries:
            lookup[delivery.match_key()] += delivery.quantity
        return lookup

    def _duplicate_invoices(self):
        duplicates = defaultdict(list)
        for invoice in self.invoices:
            duplicates[(invoice.vendor_id, invoice.invoice_number)].append(invoice)
        return {key: items for key, items in duplicates.items() if len(items) > 1}

    def _risk_score(self, financial_impact, quantity_delta, price_delta, duplicate_invoice, missing_po):
        score = 15

        if missing_po:
            score += 20
        if duplicate_invoice:
            score += 25
        if abs(quantity_delta) > 0:
            score += min(30, max(10, abs(quantity_delta) * 3))
        if abs(price_delta) > 0:
            score += min(25, max(8, abs(price_delta) * 35))
        score += min(20, int(financial_impact / 250))
        return max(0, min(score, 100))

    def _priority_for_score(self, score):
        if score >= 75:
            return "Critical"
        if score >= 50:
            return "High"
        if score >= 25:
            return "Medium"
        return "Low"

    def _build_case_type(self, missing_po, duplicate_invoice, quantity_delta, price_delta):
        if duplicate_invoice:
            return "duplicate_invoice"
        if missing_po:
            return "missing_po_match"
        if abs(quantity_delta) > 0 and abs(price_delta) > 0:
            return "quantity_and_price_mismatch"
        if abs(quantity_delta) > 0:
            return "quantity_mismatch"
        if abs(price_delta) > 0:
            return "price_mismatch"
        return "invoice_exception"

    def investigate(self):
        po_lookup = self._po_lookup()
        delivery_lookup = self._delivery_lookup()
        duplicate_groups = self._duplicate_invoices()

        cases = []
        seen = set()

        for invoice in self.invoices:
            key = (invoice.vendor_id, invoice.invoice_number, invoice.po_number, invoice.item_code)
            if key in seen:
                continue
            seen.add(key)

            po_match = None
            order_matches = po_lookup.get((invoice.vendor_id, invoice.po_number, invoice.item_code), [])
            if order_matches:
                po_match = order_matches[0]

            delivery_total = delivery_lookup.get((invoice.vendor_id, invoice.po_number, invoice.item_code), 0.0)
            expected_quantity = delivery_total if delivery_total > 0 else (po_match.quantity if po_match else invoice.quantity)
            expected_price = po_match.unit_price if po_match else 0.0

            quantity_delta = invoice.quantity - expected_quantity
            price_delta = invoice.unit_price - expected_price

            duplicate_invoice = (invoice.vendor_id, invoice.invoice_number) in duplicate_groups
            missing_po = po_match is None

            qty_tol = self.tolerance.quantity_threshold(expected_quantity)
            price_tol = self.tolerance.price_threshold(expected_price)

            reasons = []
            if missing_po:
                reasons.append("No matching purchase order line found")
            if abs(quantity_delta) > qty_tol:
                reasons.append(f"Quantity mismatch: {quantity_delta:+.2f} units")
            if abs(price_delta) > price_tol:
                reasons.append(f"Price mismatch: {price_delta:+.2f} per unit")
            if duplicate_invoice:
                reasons.append("Duplicate invoice detected")

            if not reasons:
                continue

            financial_impact = abs(quantity_delta * expected_price) + abs(price_delta * invoice.quantity)
            if missing_po and invoice.quantity == 0:
                financial_impact = 0.0

            score = self._risk_score(financial_impact, quantity_delta, price_delta, duplicate_invoice, missing_po)
            priority = self._priority_for_score(score)
            case_type = self._build_case_type(missing_po, duplicate_invoice, quantity_delta, price_delta)

            case = DiscrepancyCase(
                vendor_id=invoice.vendor_id,
                po_number=invoice.po_number,
                invoice_number=invoice.invoice_number,
                item_code=invoice.item_code,
                expected_quantity=expected_quantity,
                invoice_quantity=invoice.quantity,
                expected_unit_price=expected_price,
                invoice_unit_price=invoice.unit_price,
                quantity_delta=quantity_delta,
                price_delta=price_delta,
                financial_impact=financial_impact,
                reasons=reasons,
                priority=priority,
                risk_score=score,
                case_type=case_type,
                review_status="new",
            )
            cases.append(case)

        cases.sort(key=lambda item: item.risk_score, reverse=True)

        summary = {
            "record_count": len(self.invoices),
            "case_count": len(cases),
            "duplicate_invoice_groups": len(duplicate_groups),
            "total_financial_impact": round(sum(case.financial_impact for case in cases), 2),
            "priority_breakdown": {
                "Critical": sum(1 for case in cases if case.priority == "Critical"),
                "High": sum(1 for case in cases if case.priority == "High"),
                "Medium": sum(1 for case in cases if case.priority == "Medium"),
                "Low": sum(1 for case in cases if case.priority == "Low"),
            },
            "largest_case": max((case.financial_impact for case in cases), default=0.0),
        }

        return {
            "summary": summary,
            "cases": [case.to_dict() for case in cases],
            "duplicate_invoices": {
                str(key): [item.invoice_number for item in items]
                for key, items in duplicate_groups.items()
            },
        }
