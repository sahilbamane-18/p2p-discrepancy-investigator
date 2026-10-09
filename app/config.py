from dataclasses import dataclass


@dataclass(frozen=True)
class ToleranceConfig:
    quantity_tolerance_pct: float = 0.02
    price_tolerance_pct: float = 0.02
    quantity_absolute_tolerance: float = 0.0
    price_absolute_tolerance: float = 0.0

    @classmethod
    def from_dict(cls, payload):
        if not payload:
            return cls()
        return cls(
            quantity_tolerance_pct=float(payload.get("quantity_tolerance_pct", 0.02)),
            price_tolerance_pct=float(payload.get("price_tolerance_pct", 0.02)),
            quantity_absolute_tolerance=float(payload.get("quantity_absolute_tolerance", 0.0)),
            price_absolute_tolerance=float(payload.get("price_absolute_tolerance", 0.0)),
        )

    def quantity_threshold(self, expected_quantity: float) -> float:
        if expected_quantity == 0:
            return self.quantity_absolute_tolerance
        return max(self.quantity_absolute_tolerance, abs(expected_quantity) * self.quantity_tolerance_pct)

    def price_threshold(self, expected_price: float) -> float:
        if expected_price == 0:
            return self.price_absolute_tolerance
        return max(self.price_absolute_tolerance, abs(expected_price) * self.price_tolerance_pct)
