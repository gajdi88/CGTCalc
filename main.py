import pandas as pd
from datetime import datetime
from ledger import Ledger
from csvloader import CSVLoader

pd.set_option('display.max_columns', None)

# Example Usage
ledger = Ledger()

ledger.add_transaction(
        transation_eid="teid",
        date="13/12/2025",
        account_name="Unknown",  # Default placeholder
        amount=123,
        transaction_type="Stock",
        stock_name="GOOG",
        quantity=132.2,
        price_per_stock=15.3,
        description="very good stock"
    )

csv_loader = CSVLoader(ledger)
csv_loader.load_csv('./data/trading23-24.csv','ii')
csv_loader.load_csv('./data/trading23-24.csv','ii')

print(ledger.transactions)