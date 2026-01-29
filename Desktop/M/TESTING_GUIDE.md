# Testing Guide

This guide explains how to run tests for the InvParser application.

## Prerequisites

1. Install dependencies:
```bash
pip install -r requirments.txt
```

2. Set environment variable for database backend (optional):
```bash
# For SQLite (default)
set DB_BACKEND=sqlite

# For PostgreSQL
set DB_BACKEND=postgres
```

## Test Files

The project includes several test files:

1. **`test_extract.py`** - Tests for the `/extract` endpoint
2. **`test_invoice_by_id.py`** - Tests for the `/invoices/{invoice_id}` endpoint
3. **`integration.py`** - Integration tests for database functionality

## Running Tests

### Run All Tests

```bash
python -m pytest test_extract.py test_invoice_by_id.py integration.py -v
```

Or using unittest:

```bash
python -m unittest discover -s . -p "test_*.py" -v
```

### Run Individual Test Files

**Test Extract Endpoint:**
```bash
python test_extract.py
```

**Test Invoice by ID:**
```bash
python test_invoice_by_id.py
```

**Integration Tests:**
```bash
python integration.py
```

### Run Specific Test Cases

```bash
# Run specific test method
python -m unittest test_extract.TestInvoiceExtractionMVC.test_extract_endpoint_success

# Run all tests in a class
python -m unittest test_extract.TestInvoiceExtractionMVC
```

## Test Structure

### 1. API Tests (`test_extract.py`, `test_invoice_by_id.py`)

These tests:
- Use FastAPI's `TestClient` to test endpoints
- Mock the OCI Document AI service (no real API calls)
- Use SQLite test database
- Test both success and error cases

**Example:**
```python
def test_extract_endpoint_success(self):
    # Mock the invoice parser
    with patch('services.invoice_parser.parse_invoice_from_pdf_enhanced', return_value=mock_data):
        client = TestClient(app.app)
        response = client.post("/extract", files={"file": ("invoice.pdf", b"pdf content", "application/pdf")})
        self.assertEqual(response.status_code, 200)
```

### 2. Integration Tests (`integration.py`)

These tests:
- Test database operations directly (queries layer)
- Use in-memory SQLite database
- Don't require FastAPI or HTTP endpoints
- Test CRUD operations

**Example:**
```python
def test_save_and_get_invoice(self):
    # Direct database operations
    save_invoice_extraction(self.db, invoice_data)
    invoice = get_invoice_by_id(self.db, "123")
    self.assertIsNotNone(invoice)
```

## Test Database

All tests use SQLite databases:
- **API Tests**: `test_mvc.db`, `test_byid.db` (file-based)
- **Integration Tests**: In-memory database (`sqlite:///:memory:`)

Test databases are automatically created and cleaned up before each test.

## Mocking OCI Document AI

The tests mock the OCI Document AI service to avoid:
- Real API calls
- API key requirements
- Network dependencies
- Costs

The mock returns predefined invoice data for testing.

## Expected Test Output

When tests pass, you should see:

```
test_extract_endpoint_success ... ok
test_extract_endpoint_invalid_confidence ... ok
test_get_invoice_by_id ... ok
test_get_invoice_not_found ... ok
test_save_and_get_invoice ... ok
test_get_invoices_by_vendor ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.123s

OK
```

## Troubleshooting

### Tests Fail with Database Errors

1. Make sure `DB_BACKEND=sqlite` is set (or unset for default)
2. Delete test database files: `test_mvc.db`, `test_byid.db`
3. Check that `db.py` is properly configured

### Import Errors

1. Make sure you're in the project root directory
2. Check that all dependencies are installed: `pip install -r requirments.txt`
3. Verify Python path includes the project directory

### Mock Errors

If mocks aren't working:
- Check that the import path matches: `services.invoice_parser.parse_invoice_from_pdf_enhanced`
- Verify the function name matches the actual implementation

## Running Tests with Coverage

To check test coverage:

```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run -m unittest discover -s . -p "test_*.py"

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
```

## Continuous Integration

For CI/CD pipelines, set:

```bash
export DB_BACKEND=sqlite
python -m unittest discover -s . -p "test_*.py" -v
```
