from ledger import Ledger
import pandas as pd
from datetime import datetime

class cgt:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        # calcs as dataframe, extending the columns of the transactions dataframe
        self.calcs = pd.DataFrame(columns=list(self.ledger.transactions.columns) + ["Tax Year", "CGT Liability"])

    def calculate_yearly_cgt_liability(self):
        transactions = self.ledger.transactions
        yearly_cgt_liability = {}
        carried_forward_losses = 0.0  # Tracks losses carried forward from previous years


        # Group transactions by tax year for sequential processing
        transactions["Tax Year"] = transactions["Date"].apply(lambda x: self.get_tax_year(x))
        grouped_transactions = transactions.groupby("Tax Year")

        for tax_year, year_transactions in grouped_transactions:
            tax_free_allowance = self.get_tax_free_allowance(tax_year)
            year_transactions = year_transactions.sort_values(by="Date")
            total_gains = 0.0
            total_losses = 0.0

            for _, transaction in year_transactions.iterrows():
                if self.is_taxable(transaction):
                    date = transaction["Date"]
                    quantity = transaction["Quantity"]
                    amount = transaction["Amount"]
                    price_per_stock = transaction["CPPS"]

                    holding = self.ledger.stock_holding_at_date(transaction["Stock Name"], date)
                    total_cost = self.ledger.stock_average_purchase_price_at_date(transaction["Stock Name"], date)

                    gain_or_loss = amount - total_cost

                    if gain_or_loss > 0:
                        total_gains += gain_or_loss
                    else:
                        total_losses += abs(gain_or_loss)  # Track absolute value of losses

            # Deduct current year's losses from gains
            net_gains = total_gains - total_losses

            # Apply carried forward losses if gains remain
            if net_gains > 0:
                net_gains -= carried_forward_losses
                carried_forward_losses = max(0.0, -net_gains)  # If net_gains goes negative, carry forward

            # If net gains are below the tax-free allowance, no tax liability for the year
            if net_gains <= tax_free_allowance:
                yearly_cgt_liability[tax_year] = 0.0
                carried_forward_losses += max(0.0, tax_free_allowance - net_gains)
            else:
                # Calculate tax liability on gains above the allowance
                taxable_gain = net_gains - tax_free_allowance
                tax_rate = self.get_tax_rate(tax_year)
                tax_liability = taxable_gain * tax_rate
                yearly_cgt_liability[tax_year] = tax_liability

                # Update the carried forward losses for the next year
                carried_forward_losses += max(0.0, -taxable_gain)

            # Record calculations in the calcs dataframe
            row_to_add = pd.DataFrame({
                "Tax Year": [tax_year],
                "Total Gains": [total_gains],
                "Total Losses": [total_losses],
                "Carried Forward Losses": [carried_forward_losses],
                "Tax-Free Allowance": [tax_free_allowance],
                "Taxable Gains": [max(0.0, net_gains - tax_free_allowance)],
                "CGT Liability": [yearly_cgt_liability[tax_year]],
            })
            self.calcs = pd.concat([self.calcs, row_to_add], ignore_index=True)

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
        return transaction["Amount"] > 0  # Example: only sell transactions are taxable

    def get_rolled_forward_losses(self, year: str) -> float:
        # Implement logic to determine rolled forward losses from previous years
        # Placeholder implementation
        return 0.0

    def get_tax_free_allowance(self, year: str) -> float:
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