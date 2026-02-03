import uvicorn
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any

from db import get_db, Base, init_db
from services.invoice_parser import parse_invoice_from_pdf_enhanced
from services.invoice_service import save_inv_extraction
from controllers.invoice_controller import InvoiceController


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup: Initialize database (supports multiple databases via DB_BACKEND env var)
    engine = init_db()
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: Add any cleanup code here if needed


app = FastAPI(lifespan=lifespan)


@app.post("/extract")
async def extract(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Extract invoice data from PDF and save to database.
    
    Uses MVC pattern:
    - View: This endpoint
    - Controller: InvoiceController (via service layer)
    - Model: Invoice, Item, Confidence models
    """
    # PDF validation
    pdf_type = file.content_type == "application/pdf"
    pdf_filename = file.filename.lower().endswith(".pdf") if file.filename else False

    if not (pdf_type or pdf_filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid document. Please upload a valid PDF invoice with high confidence."
        )

    # Read PDF bytes
    pdf_bytes = await file.read()

    # Parse invoice using service layer
    try:
        extracted_data = parse_invoice_from_pdf_enhanced(pdf_bytes)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing invoice: {str(e)}"
        )

    # Save to database using service layer (which uses controller)
    try:
        save_inv_extraction(extracted_data, db)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    return extracted_data


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/invoices/vendor/{vendor_name}")
async def invoices_by_vendor(vendor_name: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieve all invoices for a specific vendor.
    
    Uses MVC pattern with InvoiceController.

    Args:
        vendor_name: The name of the vendor to filter invoices by.

    Returns:
        A dictionary containing:
            - VendorName: The vendor name (or "Unknown Vendor" if no invoices found)
            - TotalInvoices: The total number of invoices for this vendor
            - invoices: A list of invoice dictionaries, each containing invoice details

    Example:
        GET /invoices/vendor/SuperStore
        Returns:
        {
            "VendorName": "SuperStore",
            "TotalInvoices": 5,
            "invoices": [...]
        }
    """
    controller = InvoiceController()
    invoices = controller.get_invoices_dict_by_vendor(vendor_name, db)

    if not invoices:
        return {
            "VendorName": "Unknown Vendor",
            "TotalInvoices": 0,
            "invoices": []
        }

    return {
        "VendorName": vendor_name,
        "TotalInvoices": len(invoices),
        "invoices": invoices
    }


@app.get("/invoices/{invoice_id}")
def get_invoice_by_id(invoice_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieve a complete invoice by its ID, including line items.
    
    Uses MVC pattern with InvoiceController.

    Args:
        invoice_id: The unique identifier of the invoice to retrieve.

    Returns:
        A dictionary containing the complete invoice data including:
            - InvoiceId, VendorName, InvoiceDate, BillingAddressRecipient,
              ShippingAddress, SubTotal, ShippingCost, InvoiceTotal
            - Items: A list of line item dictionaries

    Example:
        GET /invoices/36259
        Returns: {"InvoiceId": "36259", "VendorName": "SuperStore", "Items": [...], ...}
    """
    controller = InvoiceController()
    invoice = controller.get_invoice_dict_by_id(invoice_id, db)

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"Invoice with ID '{invoice_id}' not found"
        )

    return invoice


if __name__ == "__main__":
    # Initialize database (supports multiple databases via DB_BACKEND env var)
    engine = init_db()
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="0.0.0.0", port=8080)
