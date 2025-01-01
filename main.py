import pandas as pd
from datetime import datetime
from ledger import Ledger
from csvloader import CSVLoader

# todo: function to give CGT percentage based on date
# todo: function to give total asset holding at a given date
# todo: function to give CGT allowance for current tax year
# todo: ledger of losses made that carry forwards
# CGT applies when selling - so calculate it for every sale
#       need cost basis for transaction - but flag if re-sold in 30 days
#       need CGT percentage
# CGT becomes liable for everything that happened in the tax year - minus allowance minus losses

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