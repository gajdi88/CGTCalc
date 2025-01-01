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
        # Append to the DataFrame
        self.transactions = pd.concat([self.transactions, pd.DataFrame([new_transaction])], ignore_index=True)

    def calculate_cgt(self) -> float:
        # logging.warning("The calculate_cgt implementation does not work yet.")

        # Calculate CGT for all transactions
        self.transactions["CGT"] = self.transactions.apply(lambda row: self._calculate_tax(row), axis=1)
        return self.transactions["CGT"].sum()

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