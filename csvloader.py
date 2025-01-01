from ledger import Ledger
import pandas as pd
# import logging

class CSVLoader:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def load_csv(self, file_path: str, template: str) -> None:
        try:
            data = pd.read_csv(file_path)

            if template == "ii":
                # Clean data by handling NaNs and formatting numbers
                data["Credit"] = data["Credit"].replace({r'[£,]': ''}, regex=True).astype(float)
                data["Debit"] = data["Debit"].replace({r'[£,]': ''}, regex=True).astype(float)
                data["Quantity"] = data["Quantity"].replace({r'[£,]': ''}, regex=True).astype(float)
                data["Price"] = data["Price"].replace({r'[£,]': ''}, regex=True).astype(float)

                mapped_data = {
                    "Date": data["Settlement Date"],
                    "Transaction External ID": data["Reference"],
                    "Stock Name": data["Sedol"],
                    "Quantity": data["Quantity"],
                    "Price Per Stock": data["Price"],
                    "Description": data["Description"],
                    "Amount": data.apply(lambda row: row["Credit"] - row["Debit"], axis=1),
                    "Transaction Type": "Stock"  # For "ii" template, all transactions are Stocks
                }

                # Create a DataFrame with mapped data
                mapped_df = pd.DataFrame(mapped_data)

                # Append transactions to ledger
                # TODO: improvement - check better if transaction not already in ledger

                for _, row in mapped_df.iterrows():
                    if row["Quantity"]>0 and row["Transaction External ID"] not in self.ledger.transactions["Transaction External ID"].values:
                        self.ledger.add_transaction(
                            transation_eid=row["Transaction External ID"],
                            date=row["Date"],
                            account_name="Unknown",  # Default placeholder
                            amount=row["Amount"],
                            transaction_type=row["Transaction Type"],
                            stock_name=row["Stock Name"],
                            quantity=row["Quantity"],
                            price_per_stock=row["Price Per Stock"],
                            description=row["Description"]
                        )
            else:
                raise ValueError("Unsupported template")

        except Exception as e:
            # logging.error(f"Error loading CSV: {e}")
            print(f"Error loading CSV: {e}")