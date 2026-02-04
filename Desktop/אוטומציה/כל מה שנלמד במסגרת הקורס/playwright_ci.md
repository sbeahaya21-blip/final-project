# Integrate Playwright tests with CI/CD pipeline

We now want to create a workflow that will trigger your Playwright tests on a certain browser.



## Using Ngrok to expose your local app

You've probably noticed that setting `localhost` URL as your app address can be problematic, because the CI workflow running in GitHub servers needs to access your app over the internet.
But your app is running locally on your machine, thus won't receive any traffic from GitHub Actions.

[Ngrok](https://ngrok.com/) is a tool used by developers to create a secure tunnel between the local machine (where the app is running) and a public URL provided by Ngrok.
Once you run an Ngrok session on your local machine, it provides you a real public domain that can be used by anyone wanting to access your local server.

### Setting up Ngrok

1. Sign up for the Ngrok service at [ngrok.com](https://ngrok.com/)

2. Install the `ngrok` agent as [described here](https://ngrok.com/docs/getting-started/#step-2-install-the-ngrok-agent)

3. Authenticate your ngrok agent. You only have to do this **once**:

```bash
ngrok config add-authtoken <your-authtoken>
```

4. Since your app will be listening on port `8082` (or whatever port you're using), start an Ngrok session by running:

```bash
ngrok http 8082
```

Your app's public URL is the URL specified in the `Forwarding` line (e.g. `https://16ae-2a06-c701-4501-3a00-ecce-30e9-3e61-3069.ngrok-free.app`).

> [!TIP]
> If you want to keep the same URL each time you use ngrok, [create a static domain on your dashboard](https://dashboard.ngrok.com/cloud-edge/domains) and then use the `--url` flag to ask the ngrok agent to use it:
> ```bash
> ngrok http 8082 --url=your-static-domain.ngrok-free.app
> ```


> [!NOTE]
> Ngrok may show a warning page before your app is loaded.
> You must manually click the "Visit Site" button, or handle it programmatically in your tests:
>
> ```python
> try:
>     page.get_by_role("button", name="Visit Site").click()
> except:
>     print("Ngrok warning page was not loaded")
> ```


## Basic workflow 

In a typical CI workflow, we would like to run UI testing when a Pull Request is opened (or an exited one is updated). 

```yaml
# .github/workflows/ui-testing.yaml
name: Playwright UI Tests

on:
  pull_request:
    branches:
     - main

  workflow_dispatch:
    inputs:
      browser:
        description: 'Browser to run tests on'
        required: true
        default: 'chrome'
        type: choice
        options:
        - chrome
        - firefox
      resolution:
        description: 'Screen resolution'
        required: true
        default: 'desktop'
        type: choice
        options:
        - desktop
        - tablet
        - mobile  
  

jobs:
  playwright-tests:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 1  # Fetch only the latest commit to speed up the checkout process
        repository: your-username/InvParserUI  # Replace with your UI testing repo
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Install Playwright browsers
      run: |
        playwright install --with-deps
        
    - name: Run Playwright tests
      env:
        HEADLESS: true
        APP_URL: https://NGROK_URL:3000
      run: |
        pytest tests/ -v
```

#### Notes


You can notice the environment variables provided to the Playwright tests:
- `APP_URL`: The URL of the application, which is used by the Playwright tests to interact with the application. Make sure to replace `NGROK_URL` with the actual public URL provided by Ngrok.
- `HEADLESS`: If set to `true`, the tests will run in **headless mode (without a GUI)**. This is useful for CI environments where no display is available.
    ```python
    from playwright.sync_api import sync_playwright
    import os
    
    headless = os.getenv('HEADLESS', 'false').lower() == 'true'
    browser = playwright.chromium.launch(headless=headless)
    page = browser.new_page()
    ```


### When to trigger the UI testing?


There are 2 main approaches, and usually testing teams implement both of them, as follows:

- The manual trigger approach allows QA engineers or developers to run UI tests on-demand, rather than automatically on every code change.
  To implement manual triggering, use the `workflow_dispatch` event. 
  This creates a "Run workflow" button in the GitHub Actions tab where you can select the browser and resolution before running the tests.

- The pull request approach automatically triggers UI tests when a PR is opened, updated, or synchronized.


## Debugging CI workflows

Debugging tests running in CI environments can be challenging since you don't see the browser and cannot debug the code interactively.

 A useful technique is to **capture screenshots** at key points in your tests and upload them as **GitHub artifacts** for later inspection.

1. Take screenshots in your tests

Add screenshot captures at critical points in your Playwright tests, especially before actions that might fail:

```python
# Take a screenshot before performing an action
self.page.screenshot(path='before_login.png')

# Take a screenshot after an error or at the end of a test
self.page.screenshot(path='after_login.png')
```

2. Upload screenshots as artifacts

Add this step to your workflow file to upload all PNG screenshots as artifacts, even if the tests fail:

```yaml
    - name: Archive test screenshots
      if: always()  # Run this step even if tests fail
      uses: actions/upload-artifact@v4
      with:
        name: test-screenshots
        path: |
          *.png
```

## Advanced workflow 

This advanced workflow runs Playwright tests in parallel across multiple browsers and screen resolutions.

The workflow uses a [matrix strategy](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations) to create multiple job combinations.

We will run 2 browsers (Chrome, Firefox) × 3 resolutions (Desktop, Tablet, Mobile) = 6 **parallel** jobs.

```yaml
# .github/workflows/ui-testing.yaml
name: Playwright UI Tests

on:
  pull_request:
    branches:
     - main

jobs:
  playwright-matrix-tests:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        browser: [chrome, firefox]
        resolution: 
          - { name: 'desktop', width: 1920, height: 1080 }
          - { name: 'tablet', width: 768, height: 1024 }
          - { name: 'mobile', width: 375, height: 667 }
      fail-fast: false  # Continue other jobs even if one fails
    
    name: Test ${{ matrix.browser }} - ${{ matrix.resolution.name }}
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 1
        repository: your-username/InvParserUI  # Replace with your UI testing repo
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Install Playwright browsers
      run: |
        playwright install --with-deps ${{ matrix.browser }}
        
    - name: Run Playwright tests
      env:
        HEADLESS: true
        BROWSER: ${{ matrix.browser }}
        SCREEN_WIDTH: ${{ matrix.resolution.width }}
        SCREEN_HEIGHT: ${{ matrix.resolution.height }}
        APP_URL: http://NGROK_URL:3000
        TEST_NAME: ${{ matrix.browser }}-${{ matrix.resolution.name }}
      run: |
        pytest tests/ -v --tb=short
        
```

Your Playwright tests should be able to handle the `BROWSER`, `SCREEN_WIDTH`, and `SCREEN_HEIGHT` environment variables to set up the browser and window size accordingly.

A common approach is to use a `BrowserFactory` class that creates the appropriate browser instance based on the environment variables. Here's an example implementation:

```python
import os
from playwright.sync_api import sync_playwright, Browser, Page

class BrowserFactory:
    def __init__(self):
        self.browser_type = os.getenv('BROWSER', 'chrome')
        self.width = int(os.getenv('SCREEN_WIDTH', '1920'))
        self.height = int(os.getenv('SCREEN_HEIGHT', '1080'))
        self.headless = os.getenv('HEADLESS', 'false').lower() == 'true'
        self.playwright = None
        self.browser = None
    
    def create_browser(self) -> Browser:
        self.playwright = sync_playwright().start()
        
        if self.browser_type == 'chrome':
            self.browser = self.playwright.chromium.launch(headless=self.headless)
        elif self.browser_type == 'firefox':
            self.browser = self.playwright.firefox.launch(headless=self.headless)
        else:
            raise ValueError(f"Unsupported browser: {self.browser_type}")
        
        return self.browser
    
    def create_page(self) -> Page:
        if not self.browser:
            self.create_browser()
        
        context = self.browser.new_context(
            viewport={'width': self.width, 'height': self.height}
        )
        page = context.new_page()
        return page
    
    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

# Usage in your tests
def get_page():
    factory = BrowserFactory()
    return factory.create_page()
```

# Exercises 

### :pencil2: Create a CI workflow for Playwright tests

Create a GitHub Actions workflow that runs your Playwright tests on multiple browsers (Chrome and Firefox) and screen resolutions (desktop, tablet, mobile) when a pull request is opened or updated.

### :pencil2: Protect branch main 

As we discussed in class, the code in the `main` branch should be protected, as it is the production code.

No one should be able to push directly to `main` branch, and all changes should be made via **pull requests**.

Thus, to protect the `main` branch:

1. **Settings** → **Branches** → **Add rule (classic)**.
2. Set branch pattern to `main`
3. Enable Require status checks and search for your workflow job names.

This ensures that the pull request cannot be merged until tests pass successfully.