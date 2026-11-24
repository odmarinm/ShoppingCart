import random

from src.models import GuestCustomer


def unique_email(first_name: str, last_name: str) -> str:
    """Unique per run: the demo store is shared by many users."""
    return f"{first_name}.{last_name}.{random.randint(100_000, 999_999)}@example.com".lower()


class GuestCustomerBuilder:
    """Builds the guest billing data. Defaults are valid values; the feature overrides what matters."""

    def __init__(self) -> None:
        self._data: dict[str, str | None] = {
            "first_name": "Ana",
            "last_name": "Lopez",
            "email": None,
            "telephone": "3001234567",
            "address_1": "Calle 100 # 15-20",
            "city": "Bogota",
            "post_code": "110111",
            "country": "Colombia",
            "region": "Bogota D.C.",
        }

    def with_names(self, first_name: str, last_name: str) -> "GuestCustomerBuilder":
        self._data["first_name"] = first_name
        self._data["last_name"] = last_name
        return self

    def with_email(self, email: str) -> "GuestCustomerBuilder":
        self._data["email"] = email
        return self

    def with_telephone(self, telephone: str) -> "GuestCustomerBuilder":
        self._data["telephone"] = telephone
        return self

    def with_address(self, address_1: str, city: str, post_code: str) -> "GuestCustomerBuilder":
        self._data["address_1"] = address_1
        self._data["city"] = city
        self._data["post_code"] = post_code
        return self

    def with_location(self, country: str, region: str) -> "GuestCustomerBuilder":
        self._data["country"] = country
        self._data["region"] = region
        return self

    def build(self) -> GuestCustomer:
        data = dict(self._data)
        data["email"] = data["email"] or unique_email(data["first_name"], data["last_name"])
        return GuestCustomer(**data)
