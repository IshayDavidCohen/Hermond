from app.modules.BusinessModule import BusinessModule
from app.modules.OrderModule import OrderModule


class OrderRepository:
    def __init__(self, order_module: OrderModule,
                 business_module: BusinessModule):
        self.order_module = order_module
        self.business_module = business_module

