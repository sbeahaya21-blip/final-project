"""API views/endpoints for invoice operations."""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
from fastapi.responses import JSONResponse
from typing import List
from app.models.invoice import Invoice
from app.models.anomaly import AnomalyResult
from app.controllers.invoice_controller import InvoiceController
from app.controllers.anomaly_controller import AnomalyController
from app.exceptions import InvoiceNotFoundError, ParsingError, InvalidInvoiceFormatError
from app.services.parser_service import ParserService
from app.services.anomaly_service import AnomalyService
from app.services.storage_service import StorageService

# Initialize services (dependency injection would be better, but keeping it simple)
storage_service = StorageService()
parser_service = ParserService()
anomaly_service = AnomalyService(storage_service)
invoice_controller = InvoiceController(parser_service, storage_service)
anomaly_controller = AnomalyController(anomaly_service, invoice_controller)

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.post("/upload", response_model=Invoice, status_code=status.HTTP_201_CREATED)
async def upload_invoice(
    file: UploadFile = File(...),
    sync_to_erpnext: bool = Query(False, description="If True, create invoice in ERPNext after parsing")
):
    """
    Upload and parse an invoice file.
    
    Args:
        file: Invoice file to upload
        sync_to_erpnext: If True, create the invoice in ERPNext after parsing
    
    Returns:
        The parsed invoice with ID.
    """
    import logging
    from app.services.erpnext_client import ERPNextClient
    from app.config import Config
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Received upload request for file: {file.filename}, sync_to_erpnext: {sync_to_erpnext}")
        file_content = await file.read()
        logger.info(f"File read successfully, size: {len(file_content)} bytes")
        
        invoice = invoice_controller.upload_and_parse_invoice(
            file_content, file.filename or "unknown"
        )
        logger.info(f"Invoice parsed successfully, ID: {invoice.id}")
        
        # Analyze invoice first to get risk score (before syncing to ERPNext)
        risk_score = None
        risk_explanation = None
        try:
            updated_invoice, analysis_result = anomaly_controller.analyze_invoice(invoice.id)
            risk_score = analysis_result.risk_score
            risk_explanation = analysis_result.explanation
            logger.info(f"Invoice analyzed - Risk Score: {risk_score}/100")
            # Update invoice with analysis results
            invoice = updated_invoice
        except Exception as e:
            logger.warning(f"Could not analyze invoice before ERPNext sync: {str(e)}")
        
        # Optionally sync to ERPNext
        if sync_to_erpnext:
            logger.info("ERPNext sync requested")
            if Config.validate_erpnext_config():
                logger.info(f"ERPNext configured: {Config.ERPNEXT_BASE_URL}")
                try:
                    erpnext_client = ERPNextClient(
                        base_url=Config.ERPNEXT_BASE_URL,
                        api_key=Config.ERPNEXT_API_KEY,
                        api_secret=Config.ERPNEXT_API_SECRET
                    )
                    logger.info("Creating Purchase Invoice in ERPNext...")
                    # Set a shorter timeout to prevent hanging
                    # Pass risk score to include it in ERPNext
                    erpnext_result = erpnext_client.create_purchase_invoice(
                        invoice.parsed_data,
                        risk_score=risk_score,
                        risk_explanation=risk_explanation
                    )
                    erpnext_invoice_name = erpnext_result.get('data', {}).get('name', 'unknown')
                    logger.info(f"✓ Invoice created in ERPNext: {erpnext_invoice_name}")
                    if risk_score is not None:
                        logger.info(f"✓ Risk score ({risk_score}/100) added to ERPNext invoice")
                        logger.info(f"  Risk explanation: {risk_explanation[:100] if risk_explanation else 'N/A'}...")
                    else:
                        logger.warning("⚠ Risk score not available - invoice was not analyzed before sync")
                    logger.info(f"✓ Invoice submitted successfully in ERPNext")
                    logger.info(f"📋 View invoice in ERPNext: {Config.ERPNEXT_BASE_URL}/app/purchase-invoice/{erpnext_invoice_name}")
                except Exception as e:
                    logger.error(f"✗ Failed to sync invoice to ERPNext: {str(e)}")
                    logger.error(f"Error type: {type(e).__name__}")
                    # Log the full error message which should contain ERPNext's error details
                    if hasattr(e, 'args') and e.args:
                        logger.error(f"Error details: {e.args}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    # Don't fail the upload if ERPNext sync fails - continue and return invoice
            else:
                logger.warning("✗ ERPNext sync requested but ERPNext not configured")
                logger.warning(f"ERPNEXT_BASE_URL: {Config.ERPNEXT_BASE_URL}")
                logger.warning(f"ERPNEXT_API_KEY set: {bool(Config.ERPNEXT_API_KEY)}")
                logger.warning(f"ERPNEXT_API_SECRET set: {bool(Config.ERPNEXT_API_SECRET)}")
        
        return invoice
    except ParsingError as e:
        logger.error(f"Parsing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process invoice: {str(e)}"
        )


@router.post("/create", response_model=Invoice, status_code=status.HTTP_201_CREATED)
async def create_invoice(invoice_data: dict):
    """
    Create an invoice from JSON data (useful for testing).
    
    Expected format:
    {
        "vendor_name": "Vendor ABC",
        "invoice_number": "INV-001",
        "invoice_date": "2024-01-15T10:00:00",
        "total_amount": 1000.0,
        "items": [
            {
                "name": "Product A",
                "quantity": 10.0,
                "unit_price": 50.0,
                "total_price": 500.0
            }
        ],
        "currency": "USD"
    }
    """
    try:
        invoice = invoice_controller.create_invoice_from_data(invoice_data)
        return invoice
    except InvalidInvoiceFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create invoice: {str(e)}"
        )


@router.get("/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: str):
    """Get invoice details by ID."""
    try:
        return invoice_controller.get_invoice(invoice_id)
    except InvoiceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("", response_model=List[Invoice])
async def list_invoices():
    """List all invoices."""
    return invoice_controller.list_invoices()


@router.post("/{invoice_id}/analyze", response_model=AnomalyResult)
async def analyze_invoice(invoice_id: str):
    """
    Analyze an invoice for anomalies and potential fraud.
    
    Returns risk score (0-100) and human-readable explanation.
    """
    try:
        invoice, anomaly_result = anomaly_controller.analyze_invoice(invoice_id)
        return anomaly_result
    except InvoiceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze invoice: {str(e)}"
        )


@router.delete("/{invoice_id}", status_code=status.HTTP_200_OK)
async def delete_invoice(invoice_id: str):
    """
    Delete an invoice by ID.
    
    Returns success message.
    """
    try:
        invoice_controller.delete_invoice(invoice_id)
        return {"message": f"Invoice {invoice_id} deleted successfully", "deleted": True}
    except InvoiceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete invoice: {str(e)}"
        )
