from unittest import TestCase
from ledger import Ledger

class TestLedger(TestCase):
    def setUp(self):
        self.ledger = Ledger()
        self.ledger.add_transaction("EID123", "2023-01-01", "Account1", 1000.0, "Stock", stock_name="AAPL", quantity=10,
                                    price_per_stock=100.0, tax_paid=0.0)
        self.ledger.add_transaction("EID124", "2023-01-03", "Account1", 500.0, "Stock", stock_name="GOOG", quantity=10,
                                    price_per_stock=50.0, tax_paid=0.0)
        self.ledger.add_transaction("EID125", "2023-01-04", "Account1", 600.0, "Stock", stock_name="GOOG", quantity=20,
                                    price_per_stock=65.0, tax_paid=0.0)

    def test_stock_holding_at_date(self):
        holding = self.ledger.stock_holding_at_date("AAPL", "2023-01-02")
        self.assertEqual(holding, 10)

    def test_stock_average_purchase_price_at_date(self):
        average_price = self.ledger.stock_average_purchase_price_at_date("GOOG", "2023-01-06")
        self.assertEqual(average_price, 60)