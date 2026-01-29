# Allure Reports

Allure Report is a popular open source tool for visualizing the results of a test run.
It produces reports that can be opened anywhere and can be read by anyone, no deep technical knowledge required.

How does it work? 

![](https://allurereport.org/images/diagrams/how-it-works.png)

1. Run your tests as you would do normally, from the command line, from your IDE, etc.
   To allow Allure to collect test results, you have to configure the **Allure adapter**. There exist adapters to all famous testing framework, including Pytest, JUnit, etc. 
2. The Allure adapter saves data in a dedicated separate directory (`allure-results` on the picture above). 
3. From the `allure-results` you can generate an HTML report, by the `allure generate` command. 

## Install Allure 

To install Allure command line tool, follow the instructions in the [official documentation](https://allurereport.org/docs/v3/install/)

## Getting started with Allure pytest 

First, add Allure dependencies to the `requirements.txt`:

```txt
allure-pytest
```

Run the test: 
```bash
pytest --alluredir=allure-results
```

> [!TIP]
> You can also add this to the `pytest.ini` file, so that you don't have to specify the `--alluredir` option every time.


Finally, convert the test results into an HTML report, 
use the `allure generate` processes the test results and saves an HTML report into the `allure-report` directory.

To view the report, use the `allure open` command.
When you execute the same tests again and again, the results are getting accumulated into the same Allure results directory, they are referred to as **retries**.

## Adding tests information 

There is a lot of [metadata](https://allurereport.org/docs/pytest/#specify-description-links-and-other-metadata) you can add to each test so that it would appear in the report. 

For example, you can add some decorators to the `test_extract_endpoint()` test in the `test/test_extract.py` file:
```python
import unittest
import allure
from allure import severity_level
from fastapi.testclient import TestClient
from app import app

class TestHealthEndpoint(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
    
    @allure.severity(severity_level.CRITICAL)
    @allure.testcase("TMS-123")
    def test_health_endpoint(self):
        """Test the /health endpoint returns ok status"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
```

You can also collect various information about the environment in which the tests were executed.
To provide environment information, put a file named `environment.properties` into the `allure-results` directory after running the tests.
See the example in [Environment file](https://allurereport.org/docs/how-it-works-environment-file/).


## Integration with CI pipelines

Allure Report has a [plugin for GitHub Actions](https://allurereport.org/docs/integrations-github/#github-actions-integration), which automatically generates test reports and publish them to the PR discussion.

Add the below configurations to your `.github/workflows/test.yml`:

```yaml
name: API Testing

on:
  pull_request:
    branches: 
      - main

permissions:
  pull-requests: write
  checks: write

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code 
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest httpx
    
    - name: Run tests
      run: |
        pytest --alluredir=allure-results -v test/
    
    - name: Run Allure Action
      uses: allure-framework/allure-action@v0
      with:
        report-directory: "./allure-report"
        github-token: ${{ secrets.GITHUB_TOKEN }}
```

# Exercises 
        
### :pencil2: Create Allure Report for your tests

1. Generate allure report for the InvParser app.
2. Add environment details to your test reports by creating an `environment.properties` file in the `allure-results` directory. The file should include:
   - `App.Version` - the version of your InvParser application (e.g., `1.0.0`)
   - `Environment` - the environment where tests are running (e.g., `development`, `staging`, `production`)
   - `Python.Version` - the Python version used for testing
   - `Test.Execution.Date` - when the tests were executed
   
   Example `environment.properties`:
   ```properties
   App.Version=1.0.0
   Environment=development
   Python.Version=3.11
   Test.Execution.Date=2026-01-07 10:30:00
   ```
   
3. Integrate the Allure Report with GitHub Actions, so that the environment data will be reported. 
