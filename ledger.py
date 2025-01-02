import pandas as pd
from datetime import datetime
# import logging

class Ledger:
    def __init__(self):
        # Initialize the DataFrame with predefined columns
        self.transactions = pd.DataFrame(columns=[
            "Transaction ID", "Date", "Account Name", "Amount",
            "Stock Name", "Quantity", "Price Per Stock", "Tax Paid", "Transaction Type"
        ])
        self.tax_years = pd.DataFrame(columns=[
            "Tax Year", "Date"
        ])

    def add_transaction(self, transation_eid: str, date: str, account_name: str, amount: float, transaction_type: str, **kwargs) -> None:
        # Determine the next Transaction ID
        next_id = self.transactions["Transaction ID"].max() + 1 if not self.transactions.empty else 1

        # Create a new transaction row
        new_transaction = {
            "Transaction ID": next_id,
            "Transaction External ID": transation_eid,
            "Date": pd.to_datetime(date),
            "Account Name": account_name,
            "Amount": amount,
            "Transaction Type": transaction_type,
            "Stock Name": kwargs.get("stock_name", None),
            "Quantity": kwargs.get("quantity", None),
            "Price Per Stock": kwargs.get("price_per_stock", None),
            "Tax Paid": kwargs.get("tax_paid", None),
        }
        if not self.transactions.empty:
            self.transactions = pd.concat([self.transactions, pd.DataFrame([new_transaction])], ignore_index=True)
        else:
            self.transactions = pd.DataFrame([new_transaction])

    def calculate_cgt_per_stock(self, stock_name) -> float:
        # WIP

        # Filter transactions for the given stock
        stock_transactions = self.transactions[self.transactions["Stock Name"] == stock_name]

        # Calculate CGT liability for each transaction
        stock_transactions["CGT Liability"] = stock_transactions.apply(self._calculate_cgt, axis=1)

        # Sum up the CGT liabilities
        total_cgt = stock_transactions["CGT Liability"].sum()

        return total_cgt


    def stock_holding_at_date(self, stock_name, date) -> float:
        # Filter transactions for the given stock
        stock_transactions = self.transactions[self.transactions["Stock Name"] == stock_name]

        # Filter transactions up to the given date
        stock_transactions = stock_transactions[stock_transactions["Date"] <= pd.to_datetime(date)]

        # Calculate the total quantity
        total_quantity = stock_transactions["Quantity"].sum()
        return total_quantity

    def stock_average_purchase_price_at_date(self, stock_name, date) -> float:
        # Filter transactions for the given stock
        stock_transactions = self.transactions[self.transactions["Stock Name"] == stock_name]

        # Filter to only buy transactions
        buy_transactions = stock_transactions[stock_transactions["Quantity"] > 0]

        # Calculate the weighted average purchase price
        if buy_transactions.empty:
            return 0
        else:
            total_quantity = buy_transactions["Quantity"].sum()
            total_cost = (buy_transactions["Quantity"] * buy_transactions["Price Per Stock"]).sum()
            average_price = total_cost / total_quantity
            return average_price

    def _calculate_tax(self, row: pd.Series) -> float:
        # Define tax calculation logic based on transaction type
        if row["Transaction Type"] == "Stock":
            if pd.notna(row["Quantity"]) and pd.notna(row["Price Per Stock"]):
                return row["Quantity"] * row["Price Per Stock"] * 0.2  # Example: 20% tax
        elif row["Transaction Type"] == "Interest":
            if pd.notna(row["Amount"]) and pd.notna(row["Tax Paid"]):
                return max(0, row["Amount"] * 0.15 - row["Tax Paid"])  # Example: 15% tax minus paid
        return 0

    def summary(self) -> None:
        # Provide a quick summary of CGT paid and outstanding
        total_cgt = self.calculate_cgt()
        total_paid = self.transactions["Tax Paid"].sum()
        outstanding = total_cgt - total_paid
        print(f"Total CGT Required: {total_cgt:.2f}")
        print(f"Total Tax Paid: {total_paid:.2f}")
        print(f"Outstanding CGT: {outstanding:.2f}")

    def filter_transactions(self, transaction_type: str = None) -> pd.DataFrame:
        # Filter transactions by type or other attributes
        if transaction_type:
            return self.transactions[self.transactions["Transaction Type"] == transaction_type]
        return self.transactions