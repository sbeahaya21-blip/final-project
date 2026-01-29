# Intro To Python Development

## Get the code 

As said, the first thing you'll probably do in your first day at work is to set up your development environment and get the code base of the project you'll be working on.

If haven't done yet, create your own copy of the InvParser project:

1. Navigate to the template repository: https://github.com/alonitac/InvParserSamana
2. Click **Use this template** → **Create a new repository**
3. Name your repository (e.g., `InvParserSamana`)
4. Click **Create repository**

Now clone your repository to your local machine:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
```

Now open the project in VSCode by **File** → **Open Folder** → Select your project folder.

## Understanding Python Execution Environments

A **Python execution environment** is where your Python code runs. It includes:

- The Python interpreter (the program that executes Python code)
- Installed packages and libraries
- Environment variables and configurations

When you run `which python`, you're checking which Python interpreter is active in your current environment.

You can open a terminal in VSCode by **Terminal** → **New Terminal**, and check the active Python interpreter.

### Create a Virtual Environment (venv)

In each Python project, we would like to have a separate environment to manage dependencies. This is called a **virtual environments (venv)**.
A **virtual environment** is an isolated Python environment for your project. It prevents dependency conflicts between different projects.

In Create a virtual environment:

```bash
python -m venv .venv
```

The `python -m venv` command executes the built-in `venv` module to create a new virtual environment.
The `.venv` argument specifies the **directory name** where the virtual environment will be created.

You'll notice a new folder named `.venv` in your project directory. This folder contains the isolated Python interpreter and all installed packages for this project.

To work with Python virtual environments, you need to **activate** them.

VScode may automatically detect the venv and suggest associating it for the workspace. Accept it. 
If not, you can manually select it by pressing `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS), typing **Python: Select Interpreter**, and choosing the one from your `.venv` folder.

To make sure the virtual environment is activated, please open a new terminal in VSCode, you should see `(.venv)` in your terminal prompt, indicating the virtual environment is active.

### Install Dependencies with `pip`

**pip** is Python's package installer.
It downloads and installs libraries from the Python Package Index (PyPI).

From a terminal **with the virtual environment activated**, run:

```bash
pip install -r requirements.txt
```

This reads `requirements.txt` line by line and installs all listed packages into your virtual environment.

To see what's installed:

```bash
pip list
```


### Running the app from the Command Line

The most simple and straightforward way to run Python code is using the command line.

You can run Python scripts directly using the `python` command:

```bash
python app.py
```


The script will execute in your active virtual environment, using all installed dependencies.

#### Debugging in VSCode

A much better way to run and debug Python code is using the built-in debugger in VSCode.

Debugging lets you pause execution, inspect variables, and step through code line-by-line.

1. Open `app.py` file in VSCode.
2. Click the **Run and Debug** icon in the left sidebar (or press `Ctrl+Shift+D`)
3. Click **Run and Debug** button.
4. In the opened panel, choose **Python File**.
5. The debugger will start, and you can set breakpoints by clicking in the gutter next to the line numbers.

# Exercises 

### :pencil2: Configure Oracle Cloud credentials

The InvParser application interacts with Oracle Cloud services, so you'll need to set up your Oracle Cloud credentials.

Carfully follow these steps to create an API key and configure your credentials:

- Log in to the Oracle Cloud Console
- Click on your profile icon (top right), then **User Settings**
- Choose the **Token and keys** tab and click on **Add API Key**
- Select the **Generate API Key Pair** option and click **Download Private Key** to save the private key file (e.g., `oci_api_key.pem`) to your machine. Make sure to store it securely, as you won't be able to download it again. NEVER store it in a Git repository.
- Once the key was downloaded, click **Add** to complete the process.
- Now, copy the provided configuration content into a file located at `~/.oci/config` on your machine. Make sure to replace the placeholders with your actual details. It should look like this:

```text
[DEFAULT]
user=ocid1.user.oc1..abcd....
fingerprint=20:3b:97:13:55:1c:2d:ee:aa:bb:cc:dd:ee:ff:00:23
tenancy=ocid1.tenancy.oc1..abcd....
region=us-ashburn-1
key_file=<path to your private keyfile> # TODO
```

- Replace `<path to your private keyfile>` with the actual path to the private key file you downloaded earlier (e.g., `/home/your-username/oci_api_key.pem` on Linux/MacOS or `C:\Users\your-username\oci_api_key.pem` on Windows).

Make sure the app is running the following command from the root directory of your project:

```bash
curl -X POST "http://127.0.0.1:8080/extract" -F "file=@invoices_sample/invoice_Aaron_Bergman_36259.pdf"
```

This command sends a POST request to the InvParser API with a sample invoice file for processing.

### :pencil2: Normalizing OCI API Output

As you may have noticed, the raw output from the OCI Document AI service contains a lot of information, some of which may not be relevant for your specific use case.

Your goal is to modify the app code to return a response as the following scheme: 

```json 
{
  "confidence": 1,   // The confidence that the provided document is an invoice
  "data": {
    "VendorName": "string",
    "VendorNameLogo": "string",
    "InvoiceId": "string",
    "InvoiceDate": "string",
    "ShippingAddress": "string",
    "BillingAddressRecipient": "string",
    "AmountDue": "number",
    "SubTotal": "number",
    "ShippingCost": "number",
    "InvoiceTotal": "number",
    "Items": [
      {
        "Description": "string",
        "Name": "string",
        "Quantity": "number",
        "UnitPrice": "number",
        "Amount": "number"
      }
    ]
  },
  "dataConfidence": {  // The confidences for each extracted field
    "VendorName": "number",
    "VendorNameLogo": "number",
    "InvoiceId": "number",
    "InvoiceDate": "number",
    "ShippingAddress": "number",
    "BillingAddressRecipient": "number",
    "AmountDue": "number",
    "SubTotal": "number",
    "ShippingCost": "number",
    "InvoiceTotal": "number"
  }
}
```

> [!TIP]
> To kickstart your implementation, you can use the [official OCI Document AI documentation](https://docs.oracle.com/en-us/iaas/api/#/en/document-understanding/20221109/AnalyzeDocumentResult/), as well as utilize the code we started writing in class:
> ```python
> data = {}
> data_confidence = {}
> 
> for page in response.data.pages:
>     if page.document_fields:
>         for field in page.document_fields:
>             field_name = field.field_label.name if field.field_label else None
>             field_confidence = field.field_label.confidence if field.field_label else None
>             field_value = field.field_value.text
>         
>             data[field_name] = field_value
>             data_confidence[field_name] = field_confidence
> ```

