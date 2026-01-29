# Playwright - Page Object Model

Over time, projects tend to accumulate large numbers of tests.
As the total number of tests increases, it becomes harder to make changes to the codebase - a single “simple” change may cause numerous tests to fail, even though the application still works properly.

## Page object model

A **page object** is a Python class that serves as an interface to a certain page in your app.
The tests then use the methods of this page object class whenever they need to interact with the UI of that page.

The benefit is that if the UI changes for the page, the tests themselves don’t need to change, only the code within the page object needs to change.
Subsequently, all changes to support that new UI are located in one place.

Let's see it in action.

Suppose you have a login page at `http://localhost:3000/login`.

A typical automated test for the login page might look like this:

```python
import unittest
from playwright.sync_api import sync_playwright

class SpotifyLoginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=False)
    
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
    
    def setUp(self):
        self.page = self.browser.new_page()
        self.page.goto("http://localhost:8082/login")

    def test_login(self):
        page = self.page

        email_field = page.locator("#email")
        email_field.fill("user@example.com")

        password_field = page.locator("#password")
        password_field.fill("password123")

        login_button = page.locator("button[type='submit']")
        login_button.click()

        success_message = page.locator("#toast-container")
        self.assertTrue(success_message.is_visible())

    def tearDown(self):
        self.page.close()
```

There are two problems with this approach.

- There is no separation between the test method and the page locators. If the app's UI changes its identifiers, layout, or how a login is input and processed, the test itself must change.
- The ID-locators would be spread in multiple tests, in all tests that had to use this login page.

Let's see how we can improve this by introducing a page object for the login page.

```python
class LoginPage:
    def __init__(self, page):
        self.page = page
        self.email_field = "#email"
        self.password_field = "#password"
        self.login_button = "button[type='submit']"
        self.success_message = "#toast-container"
        
        if "Login" not in self.page.title():
            raise Exception("Login page not loaded successfully")

    def login_as_valid_user(self, username, password):
        self.page.locator(self.email_field).fill(username)
        self.page.locator(self.password_field).fill(password)
        self.page.locator(self.login_button).click()
        return DashboardPage(self.page)


class DashboardPage:
    def __init__(self, page):
        self.page = page
        self.home_hello_message = "#home-hello-message"
        
        if "Home" not in self.page.title():
            raise Exception("Home page not loaded successfully")
    
    def get_hello_message(self):
        return self.page.locator(self.home_hello_message).inner_text()

    def go_to_songs(self):
        self.page.locator("#nav-songs").click()
        return SongsPage(self.page)
```

So now, the login test would use this page object as follows:

```python
class SpotifyLoginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=False)
    
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
    
    def setUp(self):
        self.page = self.browser.new_page()
        self.page.goto("http://localhost:3000/login")
        self.login_page = LoginPage(self.page)

    def test_valid_login(self):
        dashboard = self.login_page.login_as_valid_user("user@example.com", "password123")

        self.assertTrue(dashboard.get_hello_message(), "Welcome, user!")

    def tearDown(self):
        self.page.close()
```

There is a lot of flexibility in how the page objects may be designed, but there are a few basic rules for getting the desired maintainability of your test code:

- The page object will contain the representation of the page. **It does not necessarily need to represent all the parts**, or the internal structure of the page. The representation should be in terms of the **services** the page provides, from the eyes of the end-user.
- Methods on the page object should return other page objects. As in our example, the `login_as_valid_user` method returns the page object of the `DashboardPage`, allows the test to perform actions on this page. 
  This means, we can effectively model the **user's journey** through our application.
- Page objects themselves should never make assertions. This is part of your test and should always be within the test's code.
  Having said that, there is one, single, verification which can, and should, be within the page object and that is to verify that the page is loaded correctly.
- If your page is rich in components, you can create a **composition of other objects**.
  This means a page object can include other objects representing specific components of the page. For example:

```python
def get_invoice(self):
    invoice_elements = self.page.locator(".invoice_item").all()
    return [InvoiceItem(e) for e in invoice_elements]


class InvoiceItem:
    def __init__(self, element):
        self.element = element

    def get_name(self):
        return self.element.locator(".item_name").inner_text()

    def get_price(self):
        return float(self.element.locator(".item_price").inner_text().replace("$", ""))
```

## Page chaining

Page chaining is a technique where methods of page objects return other page objects, allowing for a fluent interface that models the user's journey through the application.

```python
def test_user_journey_through_ecommerce_app(self):
    login_page = LoginPage(self.page)
    order_confirmation_message = 
        login_page
        .login_as_valid_user("testuser", "password123")  # returns DashboardPage
        .go_to_product_page()  # returns ProductPage
        .add_product_to_cart_and_checkout("Laptop")  # returns CheckoutPage
        .process_payment("4111111111111111", "12/25", "123")  # returns OrderConfirmationPage
        .get_order_confirmation()
    
    self.assertEqual("Thank you for your order!", order_confirmation_message)
```

In this testing style, each method belongs to some page object, and returns another page object.
This makes the test script concise and easy to follow.

