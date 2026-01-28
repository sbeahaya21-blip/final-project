"""Storage service for invoices (in-memory for simplicity)."""
from typing import Dict, List, Optional
from app.models.invoice import Invoice
from app.exceptions import InvoiceNotFoundError


class StorageService:
    """In-memory storage service for invoices."""
    
    def __init__(self):
        self._invoices: Dict[str, Invoice] = {}
    
    def save(self, invoice: Invoice) -> Invoice:
        """Save an invoice."""
        self._invoices[invoice.id] = invoice
        return invoice
    
    def get(self, invoice_id: str) -> Invoice:
        """Get an invoice by ID."""
        if invoice_id not in self._invoices:
            raise InvoiceNotFoundError(f"Invoice {invoice_id} not found")
        return self._invoices[invoice_id]
    
    def get_all(self) -> List[Invoice]:
        """Get all invoices."""
        return list(self._invoices.values())
    
    def get_by_vendor(self, vendor_name: str) -> List[Invoice]:
        """Get all invoices for a specific vendor."""
        return [
            invoice for invoice in self._invoices.values()
            if invoice.parsed_data.vendor_name.lower() == vendor_name.lower()
        ]
    
    def update(self, invoice_id: str, **updates) -> Invoice:
        """Update an invoice."""
        invoice = self.get(invoice_id)
        for key, value in updates.items():
            setattr(invoice, key, value)
        return invoice
    
    def delete(self, invoice_id: str) -> bool:
        """Delete an invoice by ID."""
        if invoice_id not in self._invoices:
            raise InvoiceNotFoundError(f"Invoice {invoice_id} not found")
        del self._invoices[invoice_id]
        return True
