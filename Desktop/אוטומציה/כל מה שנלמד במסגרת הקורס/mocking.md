# Mocking in Python

A **mock object** substitutes and imitates a real object within a testing environment. Mocking allows you to:
- Test code in isolation without relying on external services
- Control unpredictable behavior (like network requests or dates)
- Simulate errors and edge cases
- Verify how your code interacts with other objects

## The `unittest.mock` library

Python's built-in `unittest.mock` library provides everything you need for mocking. The two main tools are:

1. **`Mock`** - A class to create mock objects
2. **`patch()`** - A function to temporarily replace real objects with mocks

## Examples working with `Mock` object

#### Creating a basic mock

```python
from unittest.mock import Mock

# Create a mock object
mock = Mock()

# Mocks automatically create attributes when accessed
mock.some_method()        # Returns a Mock
mock.some_attribute       # Returns a Mock
```


#### Setting return values

Use `.return_value` to control what a mock returns:

```python
from unittest.mock import Mock

# Create a mock
calculator = Mock()

# Set the return value
calculator.add.return_value = 10

# Now calling add() returns 10
result = calculator.add(5, 5)
print(result)  # Output: 10
```

#### Using assertions

Mocks track how they were called. Use assertion methods to verify:

```python
from unittest.mock import Mock

# Create and use a mock
db = Mock()
db.get_data("users", limit=10)

# Assert it was called
db.get_data.assert_called()                              # Passes
db.get_data.assert_called_once()                         # Passes
db.get_data.assert_called_with("users", limit=10)        # Passes
db.get_data.assert_called_once_with("users", limit=10)   # Passes
```


#### Using `side_effect`

`side_effect` lets you:
- Raise exceptions
- Return different values on successive calls
- Run custom functions

```python
from unittest.mock import Mock
from requests.exceptions import Timeout

requests = Mock()
requests.get.side_effect = Timeout  # Will raise Timeout when called

try:
    requests.get("http://example.com")
except Timeout:
    print("Request timed out!")
```

Another example:

```python
from unittest.mock import Mock

mock = Mock()
mock.get.side_effect = [1, 2, 3]  # Returns 1, then 2, then 3

print(mock.get())  # 1
print(mock.get())  # 2
print(mock.get())  # 3
```


## Examples using the `patch()` function

`patch()` temporarily replaces an object with a mock during a test:

```python
import unittest
from unittest.mock import patch
from requests.exceptions import Timeout

# Your module (my_module.py)
def fetch_data():
    import requests
    response = requests.get("http://api.example.com/data")
    return response.json()

# Your test
class TestFetchData(unittest.TestCase):
    
    @patch("my_module.requests")
    def test_fetch_data_timeout(self, mock_requests):
        # Configure the mock
        mock_requests.get.side_effect = Timeout
        
        # Test that timeout is raised
        with self.assertRaises(Timeout):
            fetch_data()
```

Another option to use `patch()`:

```python
from unittest.mock import patch

def test_something():
    with patch("my_module.requests") as mock_requests:
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.json.return_value = {"key": "value"}
        
        # Your test code here
        # The mock is active only inside this block
```

When you only want to mock a specific method:

```python
from unittest.mock import patch
import requests

class TestAPI(unittest.TestCase):
    
    @patch.object(requests, "get")
    def test_get_request(self, mock_get):
        mock_get.return_value.status_code = 200
        
        response = requests.get("http://example.com")
        assert response.status_code == 200
```
