from dataclasses import dataclass


@dataclass(frozen=True)
class GuestCustomer:
    """Billing data entered in Step 2 of the guest checkout."""

    first_name: str
    last_name: str
    email: str
    telephone: str
    address_1: str
    city: str
    post_code: str
    country: str
    region: str
