from app.modules.Business import BusinessModule


class BusinessService(BusinessModule):
    def __init__(self, db):
        super().__init__(db)
