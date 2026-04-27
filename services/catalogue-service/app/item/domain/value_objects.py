from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str


@dataclass(frozen=True)
class CustomPrice:
    business_id: str
    price: float
