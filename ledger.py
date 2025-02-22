import pandas as pd
from datetime import datetime
# import logging
from typing import Optional, Dict, Any

class Ledger:
    def __init__(self):
        # Initialize the DataFrame with predefined columns
        self.transactions = pd.DataFrame(columns=[
            "Transaction ID","Transaction External ID", "Date", "Account Name", "Amount",
            "Stock Name", "Quantity", "Price Per Stock", "Tax Paid", "Transaction Type",
            "CPPS"
        ])
        self.tax_years = pd.DataFrame(columns=[
            "Tax Year", "Date"
        ])

    def add_transaction(
        self,
        transaction_eid: str,
        date: str,
        account_name: str,
        amount: float,
        transaction_type: str,
        **kwargs: Any
    ) -> None:
        """Add a new transaction to the ledger.
        
        Args:
            transaction_eid: External ID for the transaction
            date: Transaction date in string format
            account_name: Name of the account
            amount: Transaction amount
            transaction_type: Type of transaction
            **kwargs: Additional transaction details
                     - stock_name (str): Name of the stock
                     - quantity (float): Number of shares
                     - price_per_stock (float): Price per share
        
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Determine the next Transaction ID
        next_id = self.transactions["Transaction ID"].max() + 1 if not self.transactions.empty else 1

        # Create a new transaction row
        new_transaction = {
            "Transaction ID": next_id,
            "Transaction External ID": transaction_eid,
            "Date": pd.to_datetime(date),
            "Account Name": account_name,
            "Amount": amount,
            "Transaction Type": transaction_type,
            "Stock Name": kwargs.get("stock_name", None),
            "Quantity": kwargs.get("quantity", None),
            "Price Per Stock": kwargs.get("price_per_stock", None),
            "Tax Paid": kwargs.get("tax_paid", None),
            "CPPS": kwargs.get("cpps", None)
        }
        if not self.transactions.empty:
            self.transactions = pd.concat([self.transactions, pd.DataFrame([new_transaction])], ignore_index=True)
        else:
            self.transactions = pd.DataFrame([new_transaction])

        # sort transactions by date
        self.transactions = self.transactions.sort_values(by="Date")


    def stock_holding_at_date(self, stock_name, date) -> float:
        # Filter transactions for the given stock
        stock_transactions = self.transactions[self.transactions["Stock Name"] == stock_name]

        # Filter transactions up to the given date
        stock_transactions = stock_transactions[stock_transactions["Date"] < pd.to_datetime(date)]

        # Calculate the total quantity
        total_quantity = stock_transactions["Quantity"].sum()
        return total_quantity

    def stock_average_purchase_price_at_date(self, stock_name, date) -> float:
        # Filter transactions for the given stock
        stock_transactions = self.transactions[self.transactions["Stock Name"] == stock_name]
        stock_transactions = stock_transactions[stock_transactions["Date"] < pd.to_datetime(date)]

        # Filter to only buy transactions
        buy_transactions = stock_transactions[stock_transactions["Amount"] < 0]

        # Calculate the weighted average purchase price
        if buy_transactions.empty:
            return 0
        else:
            # total_quantity = buy_transactions["Quantity"].sum()
            total_cost = (buy_transactions["Amount"]).sum()

            return abs(total_cost)


    def filter_transactions(self, transaction_type: str = None) -> pd.DataFrame:
        # Filter transactions by type or other attributes
        if transaction_type:
            return self.transactions[self.transactions["Transaction Type"] == transaction_type]
        return self.transactions