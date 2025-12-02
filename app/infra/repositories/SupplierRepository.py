from app.modules.Category import CategoryModule
from app.modules.Item import ItemModule
from app.modules.Supplier import SupplierModule


class SupplierRepository:
    def __init__(self, supplier_module: SupplierModule, category_module: CategoryModule, item_module: ItemModule):
        self.supplier_module = supplier_module
        self.category_module = category_module
        self.item_module = item_module
