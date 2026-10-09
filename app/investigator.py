from collections import defaultdict

from app.models import DiscrepancyCase


class DiscrepancyInvestigator:
    def __init__(self, purchase_orders, deliveries, invoices):
        self.purchase_orders = purchase_orders
        self.deliveries = deliveries
        self.invoices = invoices

    def _po_lookup(self):
        lookup = defaultdict(list)
        for order in self.purchase_orders:
            lookup[(order.vendor_id, order.po_number, order.item_code)].append(order)
        return lookup

    def _delivery_lookup(self):
        lookup = defaultdict(float)
        for delivery in self.deliveries:
            key = (delivery.vendor_id, delivery.po_number, delivery.item_code)
            lookup[key] += delivery.quantity
        return lookup

    def _duplicate_invoices(self):
        duplicates = defaultdict(list)
        for invoice in self.invoices:
            key = (invoice.vendor_id, invoice.invoice_number)
            duplicates[key].append(invoice)
        return {key: items for key, items in duplicates.items() if len(items) > 1}

    def _score_case(self, financial_impact, quantity_delta, price_delta, duplicate_invoice):
        score = 15

        if duplicate_invoice:
            score += 25
        if abs(quantity_delta) > 0:
            score += 30 + min(25, abs(quantity_delta) * 2)
        if abs(price_delta) > 0:
            score += 15 + min(25, abs(price_delta) * 20)

        score += min(20, int(financial_impact / 100))
        score = max(0, min(score, 100))
        return score

    def _priority_for_score(self, score):
        if score >= 75:
            return "Critical"
        if score >= 50:
            return "High"
        if score >= 25:
            return "Medium"
        return "Low"

    def investigate(self):
        po_lookup = self._po_lookup()
        delivery_lookup = self._delivery_lookup()
        duplicate_invoices = self._duplicate_invoices()

        cases = []
        seen_invoice_keys = set()

        for invoice in self.invoices:
            invoice_key = (invoice.vendor_id, invoice.invoice_number, invoice.po_number, invoice.item_code)
            if invoice_key in seen_invoice_keys:
                continue
            seen_invoice_keys.add(invoice_key)

            order_matches = po_lookup.get((invoice.vendor_id, invoice.po_number, invoice.item_code), [])
            match = order_matches[0] if order_matches else None

            delivery_quantity = delivery_lookup.get((invoice.vendor_id, invoice.po_number, invoice.item_code), 0.0)
            expected_quantity = delivery_quantity if delivery_quantity > 0 else (match.quantity if match else 0.0)
            expected_price = match.unit_price if match else 0.0

            quantity_delta = invoice.quantity - expected_quantity
            price_delta = invoice.unit_price - expected_price

            reasons = []
            if match is None:
                reasons.append("No matching purchase order line found")
            if abs(quantity_delta) > 0:
                reasons.append(f"Quantity mismatch: {quantity_delta:+.2f} units")
            if abs(price_delta) > 0:
                reasons.append(f"Price mismatch: {price_delta:+.2f} per unit")

            duplicate_invoice = (invoice.vendor_id, invoice.invoice_number) in duplicate_invoices
            if duplicate_invoice:
                reasons.append("Duplicate invoice detected")

            financial_impact = abs(quantity_delta * invoice.unit_price) + abs(price_delta * invoice.quantity)
            if match is None and invoice.quantity == 0:
                financial_impact = 0.0

            score = self._score_case(financial_impact, quantity_delta, price_delta, duplicate_invoice)
            priority = self._priority_for_score(score)

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
            )
            if reasons:
                cases.append(case)

        cases.sort(key=lambda item: item.risk_score, reverse=True)

        summary = {
            "record_count": len(self.invoices),
            "case_count": len(cases),
            "duplicate_invoice_groups": len(duplicate_invoices),
            "total_financial_impact": round(sum(case.financial_impact for case in cases), 2),
            "priority_breakdown": {
                "Critical": sum(1 for case in cases if case.priority == "Critical"),
                "High": sum(1 for case in cases if case.priority == "High"),
                "Medium": sum(1 for case in cases if case.priority == "Medium"),
                "Low": sum(1 for case in cases if case.priority == "Low"),
            },
            "largest_case": max((case.financial_impact for case in cases), default=0.0),
        }

        return {"summary": summary, "cases": [case.to_dict() for case in cases], "duplicate_invoices": {str(k): [item.invoice_number for item in items] for k, items in duplicate_invoices.items()}}
