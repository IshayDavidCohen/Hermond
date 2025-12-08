from app.modules.BusinessModule import BusinessModule


class BusinessService(BusinessModule):
    def __init__(self, db):
        super().__init__(db)
