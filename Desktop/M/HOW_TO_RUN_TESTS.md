# How to Run Tests

## Quick Start

### Option 1: Run All Tests with unittest (Recommended)

```bash
# Run all test files
python -m unittest discover -s . -p "test_*.py" -v

# Or use the helper script
python run_tests.py
```

### Option 2: Run Individual Test Files

```bash
# Test extract endpoint
python test_extract.py

# Test invoice by ID endpoint
python test_invoice_by_id.py

# Integration tests
python integration.py
```

### Option 3: Run with pytest

```bash
# Run all test files
pytest test_extract.py test_invoice_by_id.py integration.py -v

# Run specific test file
pytest test_extract.py -v

# Run specific test method
pytest test_extract.py::TestInvoiceExtractionMVC::test_extract_endpoint_success -v
```

## Test Files Location

All test files are in the **root directory**:
- `test_extract.py` - Tests for `/extract` endpoint
- `test_invoice_by_id.py` - Tests for `/invoices/{id}` endpoint  
- `integration.py` - Database integration tests

**Note:** There is NO `test/` directory - tests are in the root!

## Examples

### Run all tests with verbose output:
```bash
python -m unittest discover -s . -p "test_*.py" -v
```

### Run specific test class:
```bash
python -m unittest test_extract.TestInvoiceExtractionMVC -v
```

### Run specific test method:
```bash
python -m unittest test_extract.TestInvoiceExtractionMVC.test_extract_endpoint_success -v
```

## Expected Output

When tests pass:
```
test_extract_endpoint_success (test_extract.TestInvoiceExtractionMVC) ... ok
test_extract_endpoint_invalid_confidence (test_extract.TestInvoiceExtractionMVC) ... ok
test_get_invoice_by_id (test_extract.TestInvoiceExtractionMVC) ... ok
test_get_invoice_not_found (test_extract.TestInvoiceExtractionMVC) ... ok
test_get_invoice_by_id_success (test_invoice_by_id.TestInvoiceById) ... ok
...

----------------------------------------------------------------------
Ran X tests in Y.YYYs

OK
```

## Troubleshooting

### If tests fail with import errors:
1. Make sure you're in the project root directory
2. Check that all dependencies are installed: `pip install -r requirments.txt`

### If database errors occur:
1. Delete test database files: `test_mvc.db`, `test_byid.db`
2. Make sure `DB_BACKEND=sqlite` (or leave unset for default)

### If mock errors occur:
- The tests mock `services.invoice_parser.parse_invoice_from_pdf_enhanced`
- Make sure the import path matches the actual module structure
