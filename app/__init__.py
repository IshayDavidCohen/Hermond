import os

from flask import Flask
from dotenv import load_dotenv

# Routes Blueprints
from app.routes.SupplierRoutes import supplier_bp
from app.routes.BusinessRoutes import business_bp
from app.routes.HandshakeRoutes import handshake_bp

# App services
from app.services.BusinessService import BusinessService
from app.services.SupplierService import SupplierService
from app.services.HandshakeService import HandshakeService

# App Modules
from app.modules.CategoryModule import CategoryModule
from app.modules.ItemModule import ItemModule
from app.modules.SupplierModule import SupplierModule
from app.modules.BusinessModule import BusinessModule
from app.modules.HandshakeModule import HandshakeModule

# App Repository
from app.infra.repositories.SupplierRepository import SupplierRepository
from app.infra.repositories.ItemRepository import ItemRepository
from app.infra.repositories.HandshakeRepository import HandshakeRepository

# Database
from app.infra.Database import Database

load_dotenv()

def create_app():
    # 1. Create the Flask app instance
    app = Flask(__name__)

    # 2. Configure the app
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["DB_NAME"] = os.getenv("mongo_db")

    # 3. Initialize the database with the given URI
    # Here we assume Database can take a URI directly. If not, adjust accordingly.
    db = Database(database_name=app.config["DB_NAME"], connection_uri=app.config["MONGO_URI"])

    # 4. Initializing base module
    category_module = CategoryModule(db)
    item_module = ItemModule(db)
    handshake_module = HandshakeModule(db)

    business_module = BusinessModule(db)
    supplier_module = SupplierModule(db)

    # 5. Initialize repositories
    supplier_repository = SupplierRepository(supplier_module=supplier_module, category_module=category_module)
    item_repository = ItemRepository(item_module=item_module)
    handshake_repository = HandshakeRepository(handshake_module=handshake_module, supplier_module=supplier_module, business_module=business_module)

    # 6. Initializing main services
    business_service = BusinessService(db)
    supplier_service = SupplierService(supplier_repository=supplier_repository, item_repository=item_repository)
    handshake_service = HandshakeService(handshake_repo=handshake_repository)

    # 5. Store the services in app.config for routes access
    app.config['business_service'] = business_service
    app.config['supplier_service'] = supplier_service
    app.config['handshake_service'] = handshake_service

    # 6. register blueprints
    app.register_blueprint(business_bp, url_prefix='/api/v1/business')
    app.register_blueprint(supplier_bp, url_prefix='/api/v1/supplier')
    app.register_blueprint(handshake_bp, url_prefix='/api/v1/handshake')

    # Return the fully configured app
    return app
