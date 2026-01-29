# services/invoice_service.py
from sqlalchemy.orm import Session
from controllers.invoice_controller import InvoiceController


def save_inv_extraction(data: dict, db: Session):
    """Service layer function to save invoice extraction data."""
    controller = InvoiceController()
    return controller.save_invoice(db, data)
