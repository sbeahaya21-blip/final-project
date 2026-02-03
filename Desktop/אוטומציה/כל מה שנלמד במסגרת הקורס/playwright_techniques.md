# Advanced Playwright Techniques

This tutorial covers advanced Playwright features that help you debug tests, handle authentication, and control time in your tests.

## Trace Viewer

The Trace Viewer is a tool that captures screenshots, network activity, console logs, and more - so you can investigate test failures and understand exactly what happened during execution.

### Recording traces

To record a trace, use the `context.tracing` API:

```python
import unittest
from playwright.sync_api import sync_playwright


class TestWithTracing(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()
    
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.context = self.browser.new_context()
        # Start tracing before creating the page
        self.context.tracing.start(screenshots=True, snapshots=True, sources=True)
        self.page = self.context.new_page()
    
    def test_invoice_upload(self):
        self.page.goto("http://localhost:3000")
        self.page.locator("#upload-button").click()
        self.page.locator("input[type='file']").set_input_files("test_invoice.pdf")
        # Test continues...
    
    def tearDown(self):
        # Stop tracing and save to file
        self.context.tracing.stop(path="traces/trace.zip")
        self.context.close()
```

The trace includes:
- **Screenshots** - Visual snapshots at each action
- **Snapshots** - Full DOM snapshots for time-travel debugging  
- **Sources** - Source code of test files
- **Network** - All network requests and responses
- **Console** - Console messages and errors

### Viewing traces

After running your test, open the trace file with:

```bash
playwright show-trace traces/trace.zip
```

This opens the interactive viewer.

**Best practice**: Record traces only on test failures to save disk space:

```python
def tearDown(self):
    # Only save trace if test failed
    if hasattr(self._outcome, 'errors') and self._outcome.errors:
        self.context.tracing.stop(path=f"traces/{self._testMethodName}_trace.zip")
    else:
        self.context.tracing.stop()
    self.context.close()
```

## Authentication

Many applications require users to log in before accessing features. Instead of logging in at the start of every test, Playwright lets you authenticate once and reuse the session across tests.

### Manual authentication with storage state

You can save authentication state (cookies, local storage) and reuse it:

```python
import unittest
from playwright.sync_api import sync_playwright
import os


class TestWithAuth(unittest.TestCase):
    AUTH_FILE = "playwright/.auth/user.json"
    
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()
        
        # Create auth directory if it doesn't exist
        os.makedirs("playwright/.auth", exist_ok=True)
        
        # Perform authentication once
        if not os.path.exists(cls.AUTH_FILE):
            cls._perform_authentication()
    
    @classmethod
    def _perform_authentication(cls):
        """Log in once and save the authentication state."""
        context = cls.browser.new_context()
        page = context.new_page()
        
        # Perform login
        page.goto("http://localhost:3000/login")
        page.locator("#email").fill("user@example.com")
        page.locator("#password").fill("password123")
        page.locator("button[type='submit']").click()
        
        # Wait for login to complete
        page.wait_for_url("**/dashboard")
        
        # Save authentication state
        context.storage_state(path=cls.AUTH_FILE)
        context.close()
    
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        # Create a new context with saved authentication state
        self.context = self.browser.new_context(storage_state=self.AUTH_FILE)
        self.page = self.context.new_page()
    
    def test_access_protected_page(self):
        # No need to log in - already authenticated!
        self.page.goto("http://localhost:3000/dashboard")
        
        welcome_msg = self.page.locator("#welcome").inner_text()
        self.assertIn("Welcome", welcome_msg)
    
    def tearDown(self):
        self.context.close()
```

## Clock

Playwright's Clock API allows you to control and manipulate time in the browser. This is essential for testing time-dependent features without waiting for real time to pass.

### Why control time?

Consider these scenarios:
- Testing a session timeout that occurs after 30 minutes
- Testing date-based features (e.g., "expires in 3 days")
- Checking scheduled notifications

Without clock control, you'd need to wait 30 minutes or modify your code. With the Clock API, you can instantly jump to any time.

### Basic clock usage

```python
import unittest
from playwright.sync_api import sync_playwright


class TestBankAccountPage(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()
    
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
    
    def test_countdown_timer(self):
        # Set the browser clock to a specific time
        self.page.clock.install(time="2024-01-01T10:00:00")
        
        self.page.goto("http://localhost:3000/dashboard")
        
        # Fast forward 20 minutes
        self.page.clock.fast_forward(20 * 60 * 1000)
        
        message = self.page.locator("#session-timeout").inner_text()
        self.assertEqual(message, "Are you still there? You will be automatically logged out in 10 minutes.")

        self.page.clock.fast_forward(10 * 60 * 1000)
        
        message = self.page.locator("#session-timeout").inner_text()
        self.assertEqual(message, "Your session has expired. Please log in again.")
    
    def tearDown(self):
        self.context.close()
```
