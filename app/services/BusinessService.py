from typing import Dict

from app.domain.entities.Business import Business
from app.infra.repositories.BusinessRepository import BusinessRepository

class BusinessService:
    def __init__(self, business_repository: BusinessRepository):
        self.business_repository = business_repository

    def create_business(self, business_data: Dict) -> str:
        return self.business_repository.create_business(business_data)

    def get_business(self, business_id: str) -> Business:
        return self.business_repository.get_business(business_id)
