from pydantic import BaseModel


class CreateItemRequest(BaseModel):
    supplier_id: str
    name: str
    category: str
    image: str
    desc: str
    base_price: float
    unit: str
    currency: str
