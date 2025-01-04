from ledger import Ledger
import pandas as pd
from datetime import datetime

class cgt:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        # calcs as dataframe, extending the columns of the transactions dataframe
        self.calcs = pd.DataFrame(columns=list(self.ledger.transactions.columns) + ["Tax Year", "CGT Liability"])


    def calculate_yearly_cgt_liability(self, tax_year: str = None):
        transactions = self.ledger.transactions
        yearly_cgt_liability = {}

        if tax_year:
            transactions = transactions[transactions.apply(lambda x: self.get_tax_year(x["Date"]) == tax_year, axis=1)]

        for stock_name in transactions["Stock Name"].unique():
            stock_transactions = transactions[transactions["Stock Name"] == stock_name]
            # sort stock transactions by date
            stock_transactions = stock_transactions.sort_values(by="Date")

            for _, transaction in stock_transactions.iterrows():
                if self.is_taxable(transaction):
                    date = transaction["Date"]
                    quantity = transaction["Quantity"]
                    price_per_stock = transaction["Price Per Stock"]

                    holding = self.ledger.stock_holding_at_date(stock_name, date)
                    avg_price = self.ledger.stock_average_purchase_price_at_date(stock_name, date)

                    gain = (price_per_stock - avg_price) * quantity
                    tax_rate = self.get_tax_rate(date)
                    tax_liability = gain * tax_rate

                    year = self.get_tax_year(date)
                    if year not in yearly_cgt_liability:
                        yearly_cgt_liability[year] = 0.0
                    yearly_cgt_liability[year] += tax_liability

        for year in yearly_cgt_liability:
            tax_allowance = self.get_tax_allowance(year)
            yearly_cgt_liability[year] = max(0, yearly_cgt_liability[year] - tax_allowance)

        return yearly_cgt_liability

    def get_tax_year(self, date: str) -> str:
        date = pd.to_datetime(date)
        year = date.year
        if date < datetime(year, 4, 6):
            return f"{year-1}/{year}"
        else:
            return f"{year}/{year+1}"

    def calculate_tax_liability(self):
        transactions = self.ledger.transactions
        tax_liability = 0.0

        for _, transaction in transactions.iterrows():
            if self.is_taxable(transaction):
                stock_name = transaction["Stock Name"]
                date = transaction["Date"]
                quantity = transaction["Quantity"]
                price_per_stock = transaction["Price Per Stock"]

                holding = self.ledger.stock_holding_at_date(stock_name, date)
                avg_price = self.ledger.stock_average_purchase_price_at_date(stock_name, date)

                gain = (price_per_stock - avg_price) * quantity
                tax_rate = self.get_tax_rate(date)
                tax_liability += gain * tax_rate

        return tax_liability

    def is_taxable(self, transaction: pd.Series) -> bool:
        # Define logic to determine if a transaction is taxable
        return transaction["Quantity"] < 0  # Example: only sell transactions are taxable

    def get_rolled_forward_losses(self, year: str) -> float:
        # Implement logic to determine rolled forward losses from previous years
        # Placeholder implementation
        return 0.0

    def get_tax_allowance(self, year: str) -> float:
        start_year = int(year.split('/')[0])
        if start_year >= 2024:
            return 3000.0
        elif start_year == 2023:
            return 6000.0
        else:
            return 12300.0

    def get_tax_rate(self, date: str) -> float:
        date = pd.to_datetime(date)
        if date < datetime(2024, 10, 30):
            return 0.20
        else:
            return 0.28