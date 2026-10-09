from dataclasses import dataclass, asdict


@dataclass
class PurchaseOrderLine:
    vendor_id: str
    po_number: str
    item_code: str
    quantity: float
    unit_price: float
    currency: str = "USD"


@dataclass
class DeliveryRecord:
    vendor_id: str
    po_number: str
    item_code: str
    quantity: float
    delivery_id: str


@dataclass
class InvoiceRecord:
    vendor_id: str
    po_number: str
    invoice_number: str
    item_code: str
    quantity: float
    unit_price: float


@dataclass
class DiscrepancyCase:
    vendor_id: str
    po_number: str
    invoice_number: str
    item_code: str
    expected_quantity: float
    invoice_quantity: float
    expected_unit_price: float
    invoice_unit_price: float
    quantity_delta: float
    price_delta: float
    financial_impact: float
    reasons: list[str]
    priority: str
    risk_score: int

    def to_dict(self):
        data = asdict(self)
        data["reasons"] = self.reasons
        return data
