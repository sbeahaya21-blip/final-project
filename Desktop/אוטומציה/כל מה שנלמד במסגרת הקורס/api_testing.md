# API Testing

API testing is a **functional testing** test type that ensures that the API endpoints function correctly, handle errors, and meet the expected behaviour. 

In this tutorial, we will explore how to test APIs built with FastAPI using Python's built-in `unittest` framework and the `TestClient` object.

But before, let's recall some main concept in tests methodologies:

#### Test analysis

Test analysis, simply said, is the activity of deciding **what to test**.

Choosing to test everything is usually impractical, due to time and resource constraints.
Hence, we need to analyze the system under test and decide which parts are most critical and require testing.

When testing APIs, writing tests that verify the functionality of the API endpoints is the most straightforward choice, as they are the main interface for users to interact with the application.

#### Test design

Test design is the process of deciding the strategy that we will use to test the system.

- Should we test our API with real database?
- Should we call OCI services during the test?
- Should we run a real app instance during the test or we'll use some "test client" that simulates the app behaviour?
- Should we verify that data was written to the DB?

Currently, our strategy is to use a real SQLite during the tests, mock the OCI service, and use FastAPI's `TestClient` to simulate app behaviour without running a real server.

#### Success criteria

Success criteria is a **clear definition** of when you have enough confident that app works correctly. 

Usually it is written in terms of **coverage**:

- **Code coverage** – lines, branches, or paths of code executed by tests
- **Requirements coverage** – all functional or business requirements are tested
- **Risk coverage** – areas with high complexity, critical business impact, or history of defects

In our case, we will focus on **API coverage** - making sure that all API endpoints and their functionalities are tested.

#### Test execution environment

Test execution environment is the setup where tests are run.

In our case, we will run the tests automatically in a **Continuous Integration (CI)** environment using **GitHub Actions**.

## API testing with FastAPI

### Install dependencies

To use TestClient, first install `httpx` in your venv: 

```bash
pip install httpx
```

### Example

Let's create a simple FastAPI application and write tests for it:

```python
# app.py

from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def home():
    return {"msg": "Hello World"}
```

Under `tests/test_app.py`, we can write tests for the above FastAPI application:


```python
import unittest
from fastapi.testclient import TestClient
from app import app  # Import the FastAPI app from app.py


class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"msg": "Hello World"})
```

In this test: 

1. We create a `TestClient` instance that allows us to make requests to our FastAPI `app`.
   The `setUp` method initializes the `TestClient` **before each test method runs**, ensuring a fresh client for each test.
2. We define a test case `test_home` that sends a GET request to the home endpoint and checks if the response status code is 200 and the response content matches the expected JSON.


# Exercises 

### :pencil2: API Testing for the InvPaser API 

In this exercise, you will write API tests for the InvParser API endpoints.

You should achieve full coverage of the API endpoints. 

