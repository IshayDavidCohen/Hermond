from app.domain.entities.Supplier import Supplier
from app.domain.entities.Handshake import Handshake

def supplier_to_carousel_item(supplier: Supplier) -> dict:
    return {
        "link": supplier.id,              # or supplier.slug, etc.
        "title": supplier.company_name,
        "desc": supplier.desc,
        "banner": supplier.banner,
        "icon": supplier.icon,
    }

def handshake_to_dict(handshake: Handshake) -> dict:
    """Handshake entity -> JSON-serializable dict."""
    def _dt(x):
        return x.isoformat() if hasattr(x, "isoformat") else x

    return {
        "id": handshake.id,
        "sender_id": handshake.sender_id,
        "recipient_id": handshake.recipient_id,
        "sender_type": handshake.sender_type,
        "recipient_type": handshake.recipient_type,
        "status": handshake.status.value,
        "created_at": _dt(handshake.created_at),
        "updated_at": _dt(handshake.updated_at),
    }