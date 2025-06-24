import os
import sys

def ensure_requests_installed():
    try:
        import requests
    except ImportError:
        import subprocess

        print("📦 'requests' not found. Setting up virtual environment and installing dependencies...")

        # Create venv if not already created
        if not os.path.exists("venv"):
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

        # Install requests in the venv
        subprocess.run(["venv/bin/pip", "install", "requests"], check=True)

        print("\n✅ Environment ready. Re-running script inside virtual environment...\n")

        # Re-run script inside the venv
        python_path = os.path.abspath("venv/bin/python")
        script_path = os.path.abspath(sys.argv[0])
        os.execv(python_path, [python_path, script_path] + sys.argv[1:])

ensure_requests_installed()

# ✅ Now it's safe to import
import requests
import csv

# ------------------ CONFIGURATION ------------------
AWS_ACCOUNTS_API = "https://chapi.cloudhealthtech.com/v1/aws_accounts"
ASSIGNMENTS_API = "https://chapi.cloudhealthtech.com/v2/aws_account_assignments"
CUSTOMER_API_BASE = "https://chapi.cloudhealthtech.com/v1/customers"

HEADERS = {
    "Accept": "application/json",
    "Authorization": "Bearer <YOUR_API_KEY_HERE>"  # Replace <YOUR_API_KEY_HERE> with your actual CH API key
}

# ------------------ HELPERS ------------------
def get_next_page_url(link_header):
    if not link_header:
        return None
    for link in link_header.split(", "):
        if 'rel="next"' in link:
            return link.split(";")[0].strip("<>")
    return None

def fetch_paginated_data(url, key):
    items = []
    while url:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        items.extend(data.get(key, []))
        url = get_next_page_url(response.headers.get("Link"))
    return items

def fetch_customer_name(client_api_id, cache={}):
    if not client_api_id:
        return "Unknown"
    if client_api_id in cache:
        return cache[client_api_id]
    try:
        resp = requests.get(f"{CUSTOMER_API_BASE}/{client_api_id}", headers=HEADERS)
        resp.raise_for_status()
        name = resp.json().get("name", "Unknown")
    except Exception as e:
        print(f"Error fetching customer {client_api_id}: {e}")
        name = "Unknown"
    cache[client_api_id] = name
    return name

# ------------------ MAIN LOGIC ------------------
def main(output_file="aws_accounts_full.csv"):
    print("🔄 Fetching all AWS accounts...")
    aws_accounts = fetch_paginated_data(f"{AWS_ACCOUNTS_API}?page=1&per_page=100", "aws_accounts")
    print(f"✅ Total AWS accounts fetched: {len(aws_accounts)}")

    print("🔄 Fetching all billing block assignments...")
    assignments = fetch_paginated_data(f"{ASSIGNMENTS_API}?page=1&per_page=100", "aws_account_assignments")
    print(f"✅ Total assignments fetched: {len(assignments)}")

    # Map assignments by owner_id
    assignments_map = {a["owner_id"]: a for a in assignments}

    print("🔄 Preparing data for CSV export...")
    output_rows = []
    for i, acct in enumerate(aws_accounts, 1):
        owner_id = acct.get("owner_id")
        assignment = assignments_map.get(owner_id)

        row = {
            "Account Name": acct.get("name", ""),
            "AWS Owner ID": owner_id,
            "AWS Name": acct.get("amazon_name", ""),
            "Account Type": acct.get("account_type", ""),
            "Payer Account Name": acct.get("cluster_name", ""),
            "Payer Account ID": assignment.get("payer_account_owner_id") if assignment else "",
            "Billing Block ID": assignment.get("id") if assignment else "",
            "Billing Block Name": assignment.get("billing_block_name") if assignment else "",
            "Billing Block Type": assignment.get("billing_block_type") if assignment else "",
            "Designated Payer Account ID": assignment.get("billing_family_owner_id") if assignment else "",
            "Billing Block Errors if Any": str(assignment["errors"]) if assignment and assignment.get("errors") else "",
            "Client API ID": assignment.get("target_client_api_id") if assignment else "",
            "Customer Name": fetch_customer_name(assignment.get("target_client_api_id")) if assignment else ""
        }

        output_rows.append(row)
        if i % 50 == 0 or i == len(aws_accounts):
            print(f"Processed {i}/{len(aws_accounts)} accounts")

    # ------------------ SAVE TO CSV ------------------
    headers = [
        "Account Name", "AWS Owner ID", "AWS Name", "Account Type", "Payer Account Name",
        "Payer Account ID", "Billing Block ID", "Billing Block Name", "Billing Block Type", "Designated Payer Account ID",
        "Billing Block Errors if Any", "Client API ID", "Customer Name"
    ]

    print(f"💾 Writing {len(output_rows)} rows to CSV: {output_file}")
    with open(output_file, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(output_rows)

    print("✅ Done! CSV export complete.")

# ------------------ ENTRY POINT ------------------
if __name__ == "__main__":
    main()
