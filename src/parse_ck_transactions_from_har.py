# You must pip install pandas before running this script
# Usage: 
## Download script and put it in a folder
## Open cmd (in windows) and cd to the folder
## Download the HAR file to the same folder for ease of use
## Run the script with the following command:
## python parse_ck_transactions_from_har.py <HAR file path> <Year to keep>

import pandas as pd
import json
from typing import List, Text

import sys

def clean_cols(cols: List[Text]):
    return [col.replace('_', ' ').title() for col in cols]

def get_date(transaction):
    return transaction['date']

def get_transaction_type_simple(transaction):
    return 'debit' if transaction['amount']['value'] < 0 else 'credit'

def get_amount(transaction):
    if 'transaction_type' in transaction:
        return abs(transaction['amount']['value'])
    else:
        transaction['transaction_type'] = get_transaction_type_simple(transaction)
        return abs(transaction['amount']['value']) 

def get_account(transaction):
    return transaction['account']['name']

def get_account_provider_name(transaction):
    return transaction['account']['providerName']

def get_transaction_type_detail(transaction):
    return transaction['category']['type']

def get_category(transaction):
    return transaction['category']['name']

def get_merchant(transaction):
    return transaction['merchant']['name']

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <HAR file path> <Year to keep>")
        return

    har_file_path = sys.argv[1]
    year_to_keep = int(sys.argv[2])

    # Check that har_file_path is a valid file
    try:
        open(har_file_path)
    except FileNotFoundError:
        print(f"File {har_file_path} not found.")
        return
    
    # Check that year_to_keep is a valid year
    if not isinstance(year_to_keep, int):
        print(f"Year to keep must be an integer. Got {year_to_keep} instead.")
        return

    ck_graphql_requests = json.load(open(har_file_path))

    transactions = []
    errors = []

    for entry in ck_graphql_requests['log']['entries']:
        try:
            transaction_temp = json.loads(entry['response']['content']['text'])['data']['prime']['transactionsHub']['transactionPage']['transactions']
            transactions.extend(transaction_temp)
        except KeyError:
            errors.append(entry)
        except json.JSONDecodeError:
            errors.append(entry)

    # Need to expand the amount, category, and merchant fields
    for i, transaction in enumerate(transactions):
        # Credit Karma specific fields
        transactions[i]['transaction_type_detail'] = get_transaction_type_detail(transaction)
        transactions[i]['merchant'] = get_merchant(transaction) # In Mint, this is the merchant
        
        # Mint specific fields
        transactions[i]['transaction_type'] = get_transaction_type_simple(transaction)
        transactions[i]['original_description'] = transactions[i]['merchant'] # In Mint, this is the merchant, so we can copy from above
        transactions[i]['labels'] = '' # No labels in Credit Karma data
        transactions[i]['notes'] = '' # No notes in Credit Karma data
        
        # Shared fields
        transactions[i]['amount'] = get_amount(transaction) # Amount has to be done after transaction type
        transactions[i]['date'] = get_date(transaction)
        transactions[i]['account_name'] = get_account(transaction)
        transactions[i]['account_provider_name'] = get_account_provider_name(transaction)
        transactions[i]['category'] = get_category(transaction)

    transaction_df = pd.DataFrame(transactions)

    # Get only transactions in the year passed to the script
    transaction_df['date'] = pd.to_datetime(transaction_df['date'])
    transaction_df = transaction_df[transaction_df['date'].dt.year == year_to_keep]

    # Get columns to keep
    columns_to_keep_mint = [
        'date', 
        'description',
        'original_description',
        'amount',
        'transaction_type',
        'category',
        'account_name',
        'labels',
        'notes'
    ]

    columns_to_keep_creditkarma = [
        'date',
        'description',
        'transaction_type',
        'transaction_type_detail',
        'amount',
        'category',
        'account_name',
        'account_provider_name',
        'merchant'
    ]

    # Remove underscores and capitalize the first letter of each word
    columns_to_keep_mint_clean = clean_cols(columns_to_keep_mint)
    columns_to_keep_creditkarma_clean = clean_cols(columns_to_keep_creditkarma)

    # Get the columns to be the same as what Mint would export
    transaction_df_mint = transaction_df.rename(columns=dict(zip(columns_to_keep_mint, columns_to_keep_mint_clean)))
    transaction_df_mint[columns_to_keep_mint_clean].to_csv(f'mint_transactions_{year_to_keep}.csv', index=False)
    transaction_df_ck = transaction_df.rename(columns=dict(zip(columns_to_keep_creditkarma, columns_to_keep_creditkarma_clean)))
    transaction_df_ck[columns_to_keep_creditkarma_clean].to_csv(f'creditkarma_transactions_{year_to_keep}.csv', index=False)

    print("Script executed successfully.")

if __name__ == "__main__":
    main()
