from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PurchaseOrderLine:
    vendor_id: str
    po_number: str
    item_code: str
    quantity: float
    unit_price: float
    currency: str = "USD"

    def match_key(self):
        return (self.vendor_id, self.po_number, self.item_code)

    def line_total(self):
        return self.quantity * self.unit_price


@dataclass(frozen=True)
class DeliveryRecord:
    vendor_id: str
    po_number: str
    item_code: str
    quantity: float
    delivery_id: str

    def match_key(self):
        return (self.vendor_id, self.po_number, self.item_code)


@dataclass(frozen=True)
class InvoiceRecord:
    vendor_id: str
    po_number: str
    invoice_number: str
    item_code: str
    quantity: float
    unit_price: float

    def match_key(self):
        return (self.vendor_id, self.po_number, self.item_code)


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
        return asdict(self)
