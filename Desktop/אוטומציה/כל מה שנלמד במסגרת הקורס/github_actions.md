# Continues Integration (CI) with GitHub Actions

Continues Integration (CI) is a software development practice where developers frequently integrate their code changes into the same branch, that later will be used to deploy the application.
Each integration is verified by an **automated tests** to detect integration errors as quickly as possible.


To achieve that, we need an **automation platform** - some server that manages and execute the automations.
We will use a platform which is part of GitHub, called **GitHub Actions**.

GitHub Actions is a continuous integration and continuous delivery (CI/CD) platform that allows you to automate your build, test, and deployment pipelines.

Let's review the `.github/workflows/test.yml` workflow file in the **InvParserSamana** repo, which is responsible for executing unittests on every pull request:

```yaml
name: API Testing

on:
  pull_request:
    branches: 
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
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
        pytest test/ -v
```

A **workflow** is a configurable automated process that will run one or more **jobs**.

Workflows are defined as a [YAML](https://learnxinyminutes.com/docs/yaml/) file located in the source code repo, in the `.github/workflows` directory in a repository.
The workflows can be configured to be running on different events in your repo, such a code push, by periodic schedule, or manually.

For GitHub to discover any GitHub Actions workflows in your repository, you must save the workflow files in a directory called `.github/workflows`.
You can give the workflow file any name you like, but you must use `.yml` or `.yaml` as the file name extension.

In the above workflow, there is one job called `test`, which runs a series of steps to set up the Python environment, install dependencies, and run tests using `pytest`.
Step are being executed one after another, and if one of the steps fails, the job will stop executing and be marked as failed.
