# controllers/invoice_controller.py
from sqlalchemy.orm import Session
from typing import List, Optional
from models import Invoice, Item, Confidence
from queries import (
    save_invoice_extraction,
    get_invoice_by_id as get_invoice_by_id_query,
    get_invoices_by_vendor as get_invoices_by_vendor_query,
    update_invoice,
    delete_invoice,
    create_item,
    get_item_by_id,
    update_item,
    delete_item,
    create_confidence,
    get_confidence_by_invoice,
    update_confidence,
    delete_confidence
)


class InvoiceController:
    """Controller for invoice-related operations following MVC pattern."""

    def save_invoice(self, db: Session, data: dict):
        """Save invoice extraction data to database."""
        return save_invoice_extraction(db, data)

    def get_invoice_by_id(self, invoice_id: str, db: Session) -> Optional[Invoice]:
        """Get invoice model by ID."""
        invoice = db.query(Invoice).filter_by(InvoiceId=invoice_id).first()
        return invoice

    def get_invoice_dict_by_id(self, invoice_id: str, db: Session) -> Optional[dict]:
        """Get invoice as dictionary by ID (includes items)."""
        return get_invoice_by_id_query(db, invoice_id)

    def get_invoices_by_vendor(self, vendor_name: str, db: Session) -> List[str]:
        """Get list of invoice IDs for a vendor."""
        invoices = db.query(Invoice).filter_by(VendorName=vendor_name).order_by(Invoice.InvoiceDate.asc()).all()
        return [inv.InvoiceId for inv in invoices]

    def get_invoices_dict_by_vendor(self, vendor_name: str, db: Session) -> List[dict]:
        """Get invoices as dictionaries for a vendor."""
        return get_invoices_by_vendor_query(db, vendor_name)

    def update_invoice(self, invoice_id: str, data: dict, db: Session):
        """Update invoice by ID."""
        return update_invoice(db, invoice_id, data)

    def delete_invoice(self, invoice_id: str, db: Session) -> bool:
        """Delete invoice by ID."""
        return delete_invoice(db, invoice_id)

    def get_items_by_invoice_id(self, invoice_id: str, db: Session) -> List[Item]:
        """Get all items for an invoice."""
        return db.query(Item).filter_by(InvoiceId=invoice_id).all()

    def create_item(self, invoice_id: str, item_data: dict, db: Session):
        """Create a new item for an invoice."""
        return create_item(db, invoice_id, item_data)

    def get_item_by_id(self, item_id: int, db: Session) -> Optional[dict]:
        """Get item by ID."""
        return get_item_by_id(db, item_id)

    def update_item(self, item_id: int, data: dict, db: Session):
        """Update item by ID."""
        return update_item(db, item_id, data)

    def delete_item(self, item_id: int, db: Session) -> bool:
        """Delete item by ID."""
        return delete_item(db, item_id)

    def get_confidence_by_invoice(self, invoice_id: str, db: Session) -> Optional[dict]:
        """Get confidence data for an invoice."""
        return get_confidence_by_invoice(db, invoice_id)

    def create_confidence(self, invoice_id: str, conf_data: dict, db: Session):
        """Create confidence data for an invoice."""
        return create_confidence(db, invoice_id, conf_data)

    def update_confidence(self, invoice_id: str, conf_data: dict, db: Session):
        """Update confidence data for an invoice."""
        return update_confidence(db, invoice_id, conf_data)

    def delete_confidence(self, invoice_id: str, db: Session) -> bool:
        """Delete confidence data for an invoice."""
        return delete_confidence(db, invoice_id)
