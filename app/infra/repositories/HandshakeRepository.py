from app.modules.SupplierModule import SupplierModule
from app.modules.BusinessModule import BusinessModule
from app.modules.HandshakeModule import HandshakeModule


class HandshakeRepository:
    def __init__(self, handshake_module: HandshakeModule, supplier_module: SupplierModule, business_module: BusinessModule):
        self.handshake_module = handshake_module
        self.supplier_module = supplier_module
        self.business_module = business_module
