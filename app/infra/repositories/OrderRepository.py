from app.modules.ItemModule import ItemModule
from app.modules.SupplierModule import SupplierModule
from app.modules.BusinessModule import BusinessModule
from app.modules.OrdersModule import OrderModule


class OrderRepository:
    def __init__(self, order_module: OrderModule, supplier_module: SupplierModule,
                 business_module: BusinessModule, item_module: ItemModule):
        self.order_module = order_module
        self.supplier_module = supplier_module
        self.business_module = business_module
        self.item_module = item_module

