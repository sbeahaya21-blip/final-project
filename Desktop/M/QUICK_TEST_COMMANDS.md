# Quick Test Commands

## Run Tests (Ignore Warnings)

The deprecation warnings you see are from dependencies (OCI SDK, circuitbreaker) and won't affect test results. They're safe to ignore.

### Run All Tests:
```bash
python -m unittest discover -s . -p "test_*.py" -v 2>/dev/null
```

### Run Individual Test File:
```bash
python test_extract.py
```

### Run with pytest (cleaner output):
```bash
pytest test_extract.py test_invoice_by_id.py integration.py -v --tb=short
```

### Suppress warnings in pytest:
```bash
pytest test_extract.py -v -W ignore::DeprecationWarning
```

## What You're Seeing

The warnings are:
- `DeprecationWarning: 'asyncio.iscoroutinefunction'` - from circuitbreaker library
- `DeprecationWarning: datetime.datetime.utcnow()` - from OCI SDK

These are **not errors** - your tests will still run and pass/fail correctly.

## Expected Complete Output

When tests complete successfully, you should see:

```
test_extract_endpoint_success ... ok
test_extract_endpoint_invalid_confidence ... ok
test_get_invoice_by_id ... ok
test_get_invoice_not_found ... ok

----------------------------------------------------------------------
Ran 4 tests in X.XXXs

OK
```

## If Tests Hang or Don't Complete

The mock might not be working. Try running just one test:

```bash
python -m unittest test_extract.TestInvoiceExtractionMVC.test_extract_endpoint_success -v
```
