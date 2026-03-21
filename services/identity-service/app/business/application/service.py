from typing import Dict

from app.business.domain.entities.business import Business
from app.business.domain.repository_interfaces import IBusinessRepository
from app.shared.exceptions import NotFoundError


class BusinessService:
    def __init__(self, business_repository: IBusinessRepository):
        self.business_repository = business_repository

    def create_business(self, business_data: Dict) -> str:
        return self.business_repository.create_business(business_data)

    def get_business(self, business_id: str) -> Business:
        business = self.business_repository.get_business(business_id)
        if not business:
            raise NotFoundError(f"Business {business_id} not found")
        return business

    def update_business(self, business_id: str, update_data: Dict) -> bool:
        if not self.business_repository.exists(business_id):
            raise NotFoundError(f"Business {business_id} not found")
        return self.business_repository.update_business(business_id, update_data)

    def delete_business(self, business_id: str) -> bool:
        if not self.business_repository.exists(business_id):
            raise NotFoundError(f"Business {business_id} not found")
        return self.business_repository.delete_business(business_id)
