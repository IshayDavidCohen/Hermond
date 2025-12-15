from app.infra.repositories.BusinessRepository import BusinessRepository

class BusinessService:
    def __init__(self, business_repository: BusinessRepository):
        self.business_repository = business_repository
