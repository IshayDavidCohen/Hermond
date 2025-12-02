from app.modules.Supplier import SupplierModule
from app.modules.Business import BusinessModule
from app.modules.Handshake import HandshakeModule


class HandshakeRepository:
    def __init__(self, handshake_module: HandshakeModule, supplier_module: SupplierModule, business_module: BusinessModule):
        self.handshake_module = handshake_module
        self.supplier_module = supplier_module
        self.business_module = business_module
