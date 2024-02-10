# Getting Transactions from CreditKarma

## Use Case

- You were a Mint user who had to switch to CreditKarma because Mint sadly was absorbed by CK.
- You have a template that you use to categorize your transactions for tax season, and you don't want to have to manually input transactions.

## Setup

### Python

Install requirements with `pip install -r requirements.txt`

### CreditKarma

- Go to the transactions page: <https://www.creditkarma.com/networth/transactions>
- Open Inspect (I'm using Firefox, so these may have different names in different browsers)
- Go to the 'Network' Tab (delete all the requests in there and reload the page to start fresh)
- Filter to 'graphql' to return only the requests that are hitting graphql
- On the transactions page, hold 'Page Down' or just scroll until you get to the bottom of the list (you may need to scroll up and down a few times initially to get it to trigger)
- Once you've gotten all the transactions you need, right click on one of the requests in the list and 'Save All as HAR'

## Usage

Run `python src/parse_ck_transactions_from_har.py <HAR Filepath> <Year>` in a terminal. Replace `<HAR Filepath>` with the path to the HAR file you saved, and `<Year>` with the year you want to parse transactions for. Note that I don't think CK only keeps transactions for 2 years and a few months.

## Outputs

- `creditkarma_transactions_{year}.csv` - with new fields that come through CK only
- `mint_transactions_{year}.csv` - with all your standard Mint fields, so your tax templates don't break
