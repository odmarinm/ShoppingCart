from enum import StrEnum


class CheckoutOption(StrEnum):
    """Values of the 'account' radio button in Step 1 of the checkout."""

    GUEST = "guest"
    REGISTER = "register"


class PaymentMethod(StrEnum):
    """Values of the payment method radio buttons in Step 5 of the checkout."""

    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cod"

    @property
    def label(self) -> str:
        """Text shown in the store: BANK_TRANSFER -> 'Bank Transfer'."""
        return self.name.replace("_", " ").title()

    @classmethod
    def from_label(cls, label: str) -> "PaymentMethod":
        """'Bank Transfer' -> BANK_TRANSFER, 'Cash On Delivery' -> CASH_ON_DELIVERY (texts shown in the store)."""
        key = label.strip().upper().replace(" ", "_")
        if key not in cls.__members__:
            raise ValueError(f"Unknown payment method '{label}'. Allowed: Bank Transfer, Cash On Delivery")
        return cls[key]
