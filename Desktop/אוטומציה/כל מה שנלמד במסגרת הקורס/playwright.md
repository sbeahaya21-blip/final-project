# UI Testing with Playwright

UI testing is a type of end-to-end testing that validates UI component or an entire application flow from the user's UI perspective.

## Installing Playwright

[Playwright](https://playwright.dev/) allows you to automate browser interactions across different browsers.


1. In your venv, install Playwright using pip:

```bash
pip install playwright pytest-playwright
```

2. Playwright requires browser binaries to run tests. Install them with:

```bash
playwright install
```

This command downloads Chromium, Firefox, and WebKit browsers.


## Example test

Now let's create a simple UI test for the InvParserUI application.

1. In your Invoice Parser UI project, create a `tests/` folder.

2. Create `tests/test_ui.py` with the following content:

```python
import unittest
from playwright.sync_api import sync_playwright


class TestInvParserUI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up the browser once for all tests in this class."""
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=False)  # headless=False to see the browser
        
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are done."""
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        """Set up before each test method."""
        self.page = self.browser.new_page()
    
    def test_page_title(self):
        """Test that the page title is correct."""
        self.page.goto("http://localhost:3000")
        title = self.page.title()
        self.assertIn("InvParser", title)


if __name__ == "__main__":
    unittest.main()
```


Let's break down what each part does:

1. **`sync_playwright()`** - Creates a Playwright instance using the synchronous API (as opposed to async)

2. **`setUpClass`** - A class method that runs **once before all tests** in the class. We use it to:
   - Start Playwright
   - Launch the browser with `headless=False` (so you can see the browser window)


3. **`tearDownClass`** - A class method that runs **once after all tests** in the class. We use it to close the browser and stop Playwright.

4. **`setUp`** - An instance method that runs **before each test method**. We use it to create a new browser page for each test.

5. **`test_page_title`** - Our actual test that:
   - Navigates to the application URL using `goto()`
   - Gets the page title using `title()`
   - Asserts that the title contains "InvParser"


Make sure your Invoice Parser UI application is running on `http://localhost:3000`, then execute the test using pytest:

```bash
pytest tests/test_ui.py -v
```

You should see the browser open, navigate to your application, and then close after the test completes.



## Writing tests 

Similar to API tests, UI tests follow a simple pattern:

1. **Perform actions** (click, fill, navigate)
2. **Assert expectations** (check that things look right)


### Actions

Most tests start by navigating to a URL:

```python
self.page.goto("http://localhost:3000")
```

To interact with elements, you need to first locate them. Playwright provides multiple ways to locate elements:

```python
# Find and click a link by its role and name
self.page.get_by_role("link", name="Get started").click()

# Find an element by text
self.page.get_by_text("Submit").click()

# Find by CSS selector
self.page.locator("#submit-btn").click()
```

Common actions are:

| Action | Description |
|--------|-------------|
| `locator.click()` | Click the element |
| `locator.fill(value)` | Fill an input field |
| `locator.check()` | Check a checkbox |
| `locator.select_option()` | Select dropdown option |
| `locator.hover()` | Hover over element |

### Assertions

Playwright provides **auto-waiting assertions** via the `expect` API. These assertions wait until the condition is met (or timeout):

```python
from playwright.sync_api import expect

# Assert page title contains text
expect(self.page).to_have_title("InvParser")

# Assert element is visible
expect(self.page.locator("#result")).to_be_visible()

# Assert element contains text
expect(self.page.locator(".message")).to_contain_text("Success")
```

Common assertions are:

| Assertion | Description |
|-----------|-------------|
| `expect(page).to_have_title()` | Page has title |
| `expect(page).to_have_url()` | Page has URL |
| `expect(locator).to_be_visible()` | Element is visible |
| `expect(locator).to_contain_text()` | Element contains text |
| `expect(locator).to_have_value()` | Input has value |
| `expect(locator).to_be_enabled()` | Element is enabled |


# Exercises

### :pencil2: User journey test

Choose a common **user journey** (end-to-end flow) in your InvParserUI application and write a test for it.

A user journey is a complete flow that a real user would perform, such as:
- Logging in
- Uploading an invoice file and viewing the parsed results


### :pencil2: Component Tests

Choose a specific **UI component or area** in your Invoice Parser UI application (e.g., the upload form, navigation bar, results table) and write comprehensive tests (not only happy path as done in user journey tests) for it.


