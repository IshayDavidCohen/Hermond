from dataclasses import dataclass


@dataclass(frozen=True)
class ContactInfo:
    email: str
    phone: str


@dataclass(frozen=True)
class Address:
    address: str
    shipping_address: str
