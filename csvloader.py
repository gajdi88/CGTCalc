from ledger import Ledger
import pandas as pd
# import logging
from werkzeug.utils import secure_filename
import os
from config import Config

class CSVLoader:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    def load_csv(self, file_path: str, template: str) -> None:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            data = pd.read_csv(file_path, dtype={"Sedol": str})
        except pd.errors.EmptyDataError:
            raise ValueError("The CSV file is empty")
        except pd.errors.ParserError:
            raise ValueError("Invalid CSV format")

        if template == "ii":
            # Clean data by handling NaNs and formatting numbers
            data["Credit"] = data["Credit"].replace({r'[£,]': ''}, regex=True).astype(float).fillna(0)
            data["Debit"] = data["Debit"].replace({r'[£,]': ''}, regex=True).astype(float).fillna(0)
            data["Quantity"] = data["Quantity"].replace({r'[£,]': ''}, regex=True).astype(float)
            data["Price"] = data["Price"].replace({r'[£,]': ''}, regex=True).astype(float)

            mapped_data = {
                "Date": data["Settlement Date"],
                "Transaction External ID": data["Reference"],
                "Stock Name": data["Sedol"],
                "Quantity": data["Quantity"],
                "Price Per Stock": data["Price"], # note, II confuses currencies in exports
                "Description": data["Description"],
                "Amount": data.apply(lambda row: row["Credit"] - row["Debit"], axis=1),
                "Transaction Type": "Stock",  # For "ii" template, all transactions are Stocks
                "CPPS": data.apply(lambda row: row["Credit"] - row["Debit"], axis=1) / data["Quantity"]
            }

            # Create a DataFrame with mapped data
            mapped_df = pd.DataFrame(mapped_data)

            # Append transactions to ledger
            # TODO: improvement - check better if transaction not already in ledger

            for _, row in mapped_df.iterrows():
                if row["Quantity"]>0 and row["Transaction External ID"] not in self.ledger.transactions["Transaction External ID"].values:
                    self.ledger.add_transaction(
                        transaction_eid=row["Transaction External ID"],
                        date=row["Date"],
                        account_name="Unknown",  # Default placeholder
                        amount=row["Amount"],
                        transaction_type=row["Transaction Type"],
                        stock_name=row["Stock Name"],
                        quantity=row["Quantity"],
                        price_per_stock=row["Price Per Stock"],
                        description=row["Description"],
                        cpps=row["CPPS"]
                    )
                    print(f"Added transaction: {row['Transaction External ID']}")
                


