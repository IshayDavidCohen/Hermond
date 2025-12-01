from app.modules.Business import BusinessModule


class BusinessAgent(BusinessModule):
    def __init__(self, db):
        super().__init__(db)
