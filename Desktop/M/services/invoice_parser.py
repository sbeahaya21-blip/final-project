# services/invoice_parser.py
import oci
import base64
import time
from fastapi import HTTPException
from datetime import datetime, timezone

doc_client = None

def _init_doc_client():
    global doc_client
    if doc_client is not None:
        return
    try:
        config = oci.config.from_file()
        doc_client = oci.ai_document.AIServiceDocumentClient(config)
    except Exception:
        doc_client = None

def get_doc_client():
    if doc_client is None:
        _init_doc_client()
    return doc_client

def parse_invoice_from_pdf(pdf_bytes: bytes):
    """Parse invoice from PDF using OCI Document AI."""
    client = get_doc_client()
    if client is None:
        raise HTTPException(status_code=500, detail="Document AI client not configured")

    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    document = oci.ai_document.models.InlineDocumentDetails(data=encoded_pdf)
    request = oci.ai_document.models.AnalyzeDocumentDetails(
        document=document,
        features=[
            oci.ai_document.models.DocumentFeature(feature_type="KEY_VALUE_EXTRACTION"),
            oci.ai_document.models.DocumentClassificationFeature(max_results=5)
        ]
    )

    start_time = time.time()
    response = client.analyze_document(request)

    data = {}
    data_confidence = {}
    items = []

    for page in response.data.pages:
        if not page.document_fields:
            continue
        for field in page.document_fields:
            field_name = field.field_label.name if field.field_label else None
            field_conf = field.field_label.confidence if field.field_label else None
            if field_name and field_name.lower() != "items":
                data[field_name] = field.field_value.value
                data_confidence[field_name] = field_conf
            else:
                item = {}
                for it in field.field_value.items:
                    for t in it.field_value.items:
                        item[t.field_label.name] = t.field_value.value
                items.append(item)

    data["Items"] = items

    # Validate document
    if response.data.detected_document_types:
        if not any(doc.confidence >= 0.9 for doc in response.data.detected_document_types):
            raise HTTPException(status_code=400, detail="Invalid document. Please upload a valid invoice.")

    return {
        "confidence": 1,
        "data": data,
        "dataConfidence": data_confidence,
        "predictionTime": time.time() - start_time
    }


def parse_invoice_from_pdf_enhanced(pdf_bytes: bytes):
    """Enhanced invoice parser with better field handling and formatting."""
    client = get_doc_client()
    if client is None:
        raise HTTPException(status_code=503, detail="OCI configuration error: Document AI client not configured")

    # Validate PDF
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Invalid document. Please upload a valid PDF invoice.")

    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    document = oci.ai_document.models.InlineDocumentDetails(data=encoded_pdf)
    request = oci.ai_document.models.AnalyzeDocumentDetails(
        document=document,
        features=[
            oci.ai_document.models.DocumentFeature(feature_type="KEY_VALUE_EXTRACTION"),
            oci.ai_document.models.DocumentClassificationFeature(max_results=5)
        ]
    )

    try:
        response = client.analyze_document(request)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail="The service is currently unavailable. Please try again later."
        )

    # Data structures
    data = {}
    data_confidence = {}
    single_item = {}
    extracted_items = []

    # Parse pages
    pages = []
    if response and hasattr(response, 'data') and response.data:
        if hasattr(response.data, 'pages') and response.data.pages:
            pages = response.data.pages

    for page in pages:
        if page and hasattr(page, 'document_fields') and page.document_fields:
            for field in page.document_fields:
                field_name = field.field_label.name if field.field_label and hasattr(
                    field.field_label, 'name') and field.field_label.name else None

                # Handle both .text and .value attributes for field_value
                field_value = None
                if field.field_value:
                    if hasattr(field.field_value, 'text') and field.field_value.text:
                        field_value = field.field_value.text
                    elif hasattr(field.field_value, 'value') and field.field_value.value is not None:
                        field_value = field.field_value.value

                # Skip if field_name is None
                if field_name is None:
                    continue

                # Date format
                if field_name == "InvoiceDate":
                    field_value = format_date(field_value)

                # Numeric / money fields
                if field_name in (
                    "InvoiceTotal",
                    "SubTotal",
                    "ShippingCost",
                    "Amount",
                    "UnitPrice",
                    "AmountDue"
                ):
                    field_value = amount_format(field_value)

                # Confidence
                field_confidence = field.field_label.confidence if field.field_label and hasattr(
                    field.field_label, 'confidence') and field.field_label.confidence is not None else 0.0

                # Handle items
                if field_name == "Items" and field.field_value and hasattr(field.field_value, 'items'):
                    extracted_items = []

                    for sub_field in field.field_value.items:
                        if not sub_field or not hasattr(sub_field, 'field_value') or not sub_field.field_value:
                            continue
                        if not hasattr(sub_field.field_value, 'items'):
                            continue

                        single_item = {}

                        for sub in sub_field.field_value.items:
                            if not sub:
                                continue

                            sub_key = sub.field_label.name if sub.field_label and hasattr(
                                sub.field_label, 'name') and sub.field_label.name else ""

                            # Handle both .text and .value attributes for sub items
                            sub_value = ""
                            if sub.field_value:
                                if hasattr(sub.field_value, 'text') and sub.field_value.text:
                                    sub_value = sub.field_value.text
                                elif hasattr(sub.field_value, 'value') and sub.field_value.value is not None:
                                    sub_value = sub.field_value.value

                            # Clean numeric fields inside items
                            if sub_key in ("Quantity", "UnitPrice", "Amount"):
                                sub_value = amount_format(sub_value)

                            if sub_key:
                                single_item[sub_key] = sub_value

                        extracted_items.append(single_item)

                    field_value = extracted_items

                if field_name:
                    data[field_name] = field_value

                    if field_name != "Items":
                        data_confidence[field_name] = field_confidence

    # Document validation
    confidence = None
    if response and hasattr(response, 'data') and response.data:
        if hasattr(response.data, 'detected_document_types') and response.data.detected_document_types:
            for doc_type in response.data.detected_document_types:
                if doc_type and hasattr(doc_type, 'confidence'):
                    confidence = doc_type.confidence
                    if confidence and confidence < 0.9:
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid document. Please upload a valid PDF invoice with high confidence."
                        )

    return {
        "confidence": confidence,
        "data": data,
        "dataConfidence": data_confidence,
    }


def format_date(date_text):
    """
    Converts date like:
    'Mar 06 2012' → '2012-03-06T00:00:00+00:00'
    """
    if not date_text:
        return ""
    try:
        dt = datetime.strptime(date_text.strip(), "%b %d %Y")
        return dt.replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        return date_text


def amount_format(value):
    """
    Removes $ , and spaces → returns float
    '$58.11' → 58.11
    '4,293.55' → 4293.55
    """
    if not value:
        return ""
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except Exception:
        return value
