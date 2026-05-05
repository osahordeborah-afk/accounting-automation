import datetime
from typing import Dict, List, Optional, Tuple
import random

class AccountingSystem:
    def __init__(self):
        # General Ledger: {entry_id: {"date": str, "account": str, "amount": float, "description": str, "type": str}}
        self.general_ledger: Dict[str, Dict] = {}

        # Bank Accounts: {account_number: {"name": str, "balance": float, "transactions": List[Dict]}}
        self.bank_accounts: Dict[str, Dict] = {}

        # Vendors: {vendor_id: {"name": str, "outstanding_balance": float, "payment_terms": int, "transactions": List[Dict]}}
        self.vendors: Dict[str, Dict] = {}

        # Inventory: {item_id: {"name": str, "quantity": int, "unit_cost": float, "total_value": float}}
        self.inventory: Dict[str, Dict] = {}

        # Budgets: {budget_id: {"name": str, "allocated": float, "actual": float, "variance": float}}
        self.budgets: Dict[str, Dict] = {}

        # Internal Controls: List[Dict]
        self.internal_controls: List[Dict] = []

        # Reports: List[Dict]
        self.reports: List[Dict] = []

        # Next IDs for auto-increment
        self.next_gl_entry_id = 1
        self.next_vendor_id = 1
        self.next_budget_id = 1
        self.next_report_id = 1

    # --- General Ledger Operations ---
    def add_gl_entry(self, account: str, amount: float, description: str, entry_type: str = "Journal") -> str:
        """Add a general ledger entry."""
        entry_id = f"GL{self.next_gl_entry_id}"
        self.general_ledger[entry_id] = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "account": account,
            "amount": amount,
            "description": description,
            "type": entry_type
        }
        self.next_gl_entry_id += 1
        return f"GL Entry {entry_id} added: {description} (₦{amount:,.2f})"

    # --- Bank Reconciliation ---
    def add_bank_account(self, account_number: str, name: str, initial_balance: float = 0.0) -> str:
        """Add a bank account to the system."""
        if account_number not in self.bank_accounts:
            self.bank_accounts[account_number] = {
                "name": name,
                "balance": initial_balance,
                "transactions": []
            }
            return f"Bank account {name} ({account_number}) added with balance: ₦{initial_balance:,.2f}"
        return f"Bank account {account_number} already exists."

    def reconcile_bank_transaction(self, account_number: str, amount: float, description: str, transaction_type: str = "Deposit") -> str:
        """Record and reconcile a bank transaction."""
        if account_number in self.bank_accounts:
            transaction = {
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "amount": amount,
                "description": description,
                "type": transaction_type,
                "reconciled": False
            }
            self.bank_accounts[account_number]["transactions"].append(transaction)
            if transaction_type == "Deposit":
                self.bank_accounts[account_number]["balance"] += amount
            else:
                self.bank_accounts[account_number]["balance"] -= amount
            return f"Transaction recorded for {self.bank_accounts[account_number]['name']}: {description} (₦{amount:,.2f})"
        return f"Bank account {account_number} not found."

    def mark_as_reconciled(self, account_number: str, transaction_index: int) -> str:
        """Mark a bank transaction as reconciled."""
        if account_number in self.bank_accounts and 0 <= transaction_index < len(self.bank_accounts[account_number]["transactions"]):
            self.bank_accounts[account_number]["transactions"][transaction_index]["reconciled"] = True
            return f"Transaction {transaction_index + 1} marked as reconciled."
        return "Invalid account or transaction index."

    # --- Vendor Payments ---
    def add_vendor(self, name: str, payment_terms: int = 30) -> str:
        """Add a vendor to the system."""
        vendor_id = f"V{self.next_vendor_id}"
        self.vendors[vendor_id] = {
            "name": name,
            "outstanding_balance": 0.0,
            "payment_terms": payment_terms,
            "transactions": []
        }
        self.next_vendor_id += 1
        return f"Vendor {name} added with ID: {vendor_id}"

    def record_vendor_invoice(self, vendor_id: str, amount: float, description: str) -> str:
        """Record an invoice from a vendor."""
        if vendor_id in self.vendors:
            self.vendors[vendor_id]["outstanding_balance"] += amount
            self.vendors[vendor_id]["transactions"].append({
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "amount": amount,
                "description": description,
                "type": "Invoice",
                "status": "Unpaid"
            })
            return f"Invoice recorded for {self.vendors[vendor_id]['name']}: ₦{amount:,.2f}"
        return f"Vendor ID {vendor_id} not found."

    def make_vendor_payment(self, vendor_id: str, amount: float, bank_account: str) -> str:
        """Process a payment to a vendor."""
        if vendor_id in self.vendors and bank_account in self.bank_accounts:
            if self.vendors[vendor_id]["outstanding_balance"] >= amount:
                if self.bank_accounts[bank_account]["balance"] >= amount:
                    # Update vendor balance
                    self.vendors[vendor_id]["outstanding_balance"] -= amount
                    self.vendors[vendor_id]["transactions"].append({
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "amount": amount,
                        "description": f"Payment from {bank_account}",
                        "type": "Payment",
                        "status": "Paid"
                    })
                    # Update bank balance
                    self.bank_accounts[bank_account]["balance"] -= amount
                    self.bank_accounts[bank_account]["transactions"].append({
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "amount": amount,
                        "description": f"Payment to {self.vendors[vendor_id]['name']}",
                        "type": "Withdrawal",
                        "reconciled": False
                    })
                    # Record GL entry
                    self.add_gl_entry(
                        account=f"Vendor Payable - {self.vendors[vendor_id]['name']}",
                        amount=-amount,
                        description=f"Payment to {self.vendors[vendor_id]['name']}",
                        entry_type="Payment"
                    )
                    return f"Payment of ₦{amount:,.2f} processed to {self.vendors[vendor_id]['name']} from {bank_account}."
                return f"Insufficient funds in {bank_account}."
            return f"Vendor {self.vendors[vendor_id]['name']} has insufficient outstanding balance."
        return "Invalid vendor ID or bank account."

    # --- Inventory Controls ---
    def add_inventory_item(self, name: str, quantity: int, unit_cost: float) -> str:
        """Add an inventory item."""
        item_id = f"INV{len(self.inventory) + 1}"
        self.inventory[item_id] = {
            "name": name,
            "quantity": quantity,
            "unit_cost": unit_cost,
            "total_value": quantity * unit_cost
        }
        return f"Inventory item {name} added with ID: {item_id}"

    def update_inventory(self, item_id: str, quantity_change: int, unit_cost: Optional[float] = None) -> str:
        """Update inventory quantity and value."""
        if item_id in self.inventory:
            if unit_cost is not None:
                self.inventory[item_id]["unit_cost"] = unit_cost
            self.inventory[item_id]["quantity"] += quantity_change
            self.inventory[item_id]["total_value"] = (
                self.inventory[item_id]["quantity"] * self.inventory[item_id]["unit_cost"]
            )
            return f"Inventory updated for {self.inventory[item_id]['name']}: {quantity_change} units."
        return f"Inventory item {item_id} not found."

    # --- Budgeting and Reporting ---
    def create_budget(self, name: str, allocated: float) -> str:
        """Create a new budget."""
        budget_id = f"B{self.next_budget_id}"
        self.budgets[budget_id] = {
            "name": name,
            "allocated": allocated,
            "actual": 0.0,
            "variance": 0.0
        }
        self.next_budget_id += 1
        return f"Budget {name} created with ID: {budget_id} (Allocated: ₦{allocated:,.2f})"

    def record_budget_expense(self, budget_id: str, amount: float, description: str) -> str:
        """Record an expense against a budget."""
        if budget_id in self.budgets:
            self.budgets[budget_id]["actual"] += amount
            self.budgets[budget_id]["variance"] = self.budgets[budget_id]["actual"] - self.budgets[budget_id]["allocated"]
            return f"Expense of ₦{amount:,.2f} recorded for {self.budgets[budget_id]['name']}. Variance: ₦{self.budgets[budget_id]['variance']:,.2f}"
        return f"Budget ID {budget_id} not found."

    def generate_management_report(self, month: str, year: str) -> Dict:
        """Generate a monthly management report with variance insights."""
        report_id = f"R{self.next_report_id}"
        total_gl_entries = len(self.general_ledger)
        total_vendor_payments = sum(
            sum(t["amount"] for t in vendor["transactions"] if t["type"] == "Payment")
            for vendor in self.vendors.values()
        )
        total_inventory_value = sum(item["total_value"] for item in self.inventory.values())
        budget_variances = {
            bid: budget["variance"]
            for bid, budget in self.budgets.items()
        }

        report = {
            "report_id": report_id,
            "month": month,
            "year": year,
            "date_generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_gl_entries": total_gl_entries,
                "total_vendor_payments": total_vendor_payments,
                "total_inventory_value": total_inventory_value,
                "budget_variances": budget_variances
            },
            "insights": [
                f"Processed {total_gl_entries} GL entries in {month} {year}.",
                f"Total vendor payments: ₦{total_vendor_payments:,.2f}.",
                f"Total inventory value: ₦{total_inventory_value:,.2f}.",
                f"Budget variances: {budget_variances}"
            ],
            "recommendations": [
                "Review budgets with variances exceeding 10% of allocated amounts.",
                "Reconcile all bank transactions by the 5th of the following month.",
                "Optimize inventory levels to reduce holding costs."
            ]
        }
        self.reports.append(report)
        self.next_report_id += 1
        return report

    def get_report(self, report_id: str) -> Optional[Dict]:
        """Retrieve a specific report by ID."""
        for report in self.reports:
            if report["report_id"] == report_id:
                return report
        return None

# --- Example Usage ---
if __name__ == "__main__":
    accounting = AccountingSystem()

    # Set up bank accounts
    print(accounting.add_bank_account("001", "First Bank of Nigeria", 5_000_000.00))
    print(accounting.add_bank_account("002", "GT Bank", 3_000_000.00))

    # Record bank transactions
    print(accounting.reconcile_bank_transaction("001", 1_000_000.00, "Customer Deposit", "Deposit"))
    print(accounting.reconcile_bank_transaction("001", 500_000.00, "Vendor Payment", "Withdrawal"))

    # Add vendors and process payments
    print(accounting.add_vendor("ABC Suppliers"))
    print(accounting.add_vendor("XYZ Distributors"))
    print(accounting.record_vendor_invoice("V1", 2_000_000.00, "Office Supplies"))
    print(accounting.make_vendor_payment("V1", 1_500_000.00, "001"))

    # Manage inventory
    print(accounting.add_inventory_item("Laptops", 50, 150_000.00))
    print(accounting.update_inventory("INV1", -5, 150_000.00))  # Sold 5 laptops

    # Create and record budget expenses
    print(accounting.create_budget("Operational Expenses", 22_000_000.00))
    print(accounting.record_budget_expense("B1", 1_500_000.00, "Office Rent"))
    print(accounting.record_budget_expense("B1", 500_000.00, "Utilities"))

    # Generate a management report
    report = accounting.generate_management_report("November", "2022")
    print("\n--- Monthly Management Report ---")
    for key, value in report.items():
        print(f"{key}: {value}")
