from app.domain.entities.Supplier import Supplier

def supplier_to_carousel_item(supplier: Supplier) -> dict:
    return {
        "link": supplier.id,              # or supplier.slug, etc.
        "title": supplier.company_name,
        "desc": supplier.desc,
        "banner": supplier.banner,
        "icon": supplier.icon,
    }