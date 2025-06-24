

````markdown
# AWS Billing Block Assignment Exporter

This Python script retrieves AWS account details and their billing block assignments from the CloudHealth API. It merges the data with customer information and exports everything into a clean CSV file.

## ✅ Features

- Automatically fetches all AWS accounts and billing block assignments.
- Resolves customer names via the CloudHealth Customer API.
- Combines metadata like account name, owner ID, block type, and more.
- Outputs a clean, labeled CSV file.
- Automatically sets up a virtual environment and installs dependencies if needed.

## 📦 Requirements

- Python 3.7+
- A valid CloudHealth API key
- Internet access

## 🔧 Setup & Usage

### 1. Clone the repository
```bash
git clone https://github.com/your-username/aws-billing-exporter.git
cd aws-billing-exporter
````

### 2. Add your CloudHealth API Key

Edit the script and replace:

```python
HEADERS = {
    "Accept": "application/json",
     "Authorization": "Bearer <YOUR_API_KEY_HERE>"  # Replace <YOUR_API_KEY_HERE> with your actual CH API key
}
```

### 3. Run the script

```bash
python3 billing_export.py
```

> The script will auto-create a `venv`, install `requests`, and re-run itself if needed.

### 4. Output

* The CSV file `aws_billing_assignments.csv` will be created in the same directory.

## 📄 Output Columns

| Column Name                 | Description                                |
| --------------------------- | ------------------------------------------ |
| Account Name                | CloudHealth account name                   |
| AWS Owner ID                | AWS account owner ID                       |
| AWS Name                    | AWS account alias/name                     |
| Account Type                | Type of account                            |
| Payer Account Name          | Cluster or payer account name              |
| Payer Account ID            | Payer account owner ID                     |
| Billing Block ID            | Unique ID of the billing block             |
| Billing Block Name          | Human-readable billing block name          |
| Billing Block Type          | Type of billing block (e.g., Consolidated) |
| Designated Payer Account ID | Designated payer ID for billing            |
| Billing Block Errors if Any | Any assignment errors                      |
| Client API ID               | CloudHealth client API ID                  |
| Customer Name               | CloudHealth customer name                  |

## 🛠 Notes

* If an account has no billing block assignment, the related fields including PayerAccountId will be blank.
* Errors will be shown in the “Billing Block Errors if Any” column.
* If the PayerAccount is assigned to Billing Block with "Family" Billing Block type, then consider all the linked accounts from that payer Account are assigned under the same billing block.


