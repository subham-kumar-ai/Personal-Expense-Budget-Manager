import csv
import os
from datetime import datetime
from unicodedata import category
import pandas as pd

CSV_FILE = "expenses.csv"
COLUMNS = ["Date", "Category", "Amount"]


def load_expenses():
    """Read expenses.csv and return a Pandas DataFrame."""
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=COLUMNS)

    try:
        df = pd.read_csv(CSV_FILE)
        for column in COLUMNS:
            if column not in df.columns:
                df[column] = pd.Series(dtype="object")
        df = df[COLUMNS]
        if not df.empty:
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
            df = df.dropna(subset=["Amount"])
        return df
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        print("Warning: expenses.csv could not be read. Starting with an empty list.")
        return pd.DataFrame(columns=COLUMNS)


def save_expenses(df):
    """Save DataFrame to CSV with the required columns."""
    df[COLUMNS].to_csv(CSV_FILE, index=False, quoting=csv.QUOTE_MINIMAL)

def get_positive_amount(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            amount = float(raw)
            if amount <= 0:
                print("Invalid amount. Amount must be a positive number.")
                return None
            return round(amount, 2)
        except ValueError:
            print("Invalid amount. Please enter a number, for example 250 or 99.50.")
            return None

def set_budget():
    global monthly_budget
    amount = get_positive_amount("Enter monthly budget: ")
    if amount is None:
        return
    monthly_budget = amount
    with open("budget.txt", "w", encoding="utf-8") as file:
        file.write(str(monthly_budget))
    print(f"Monthly budget set: {monthly_budget:.0f}" if monthly_budget.is_integer()
          else f"Monthly budget set: {monthly_budget:.2f}")

def load_budget():
    if os.path.exists("budget.txt"):
        try:
            with open("budget.txt", "r", encoding="utf-8") as file:
                amount = float(file.read().strip())
                if amount > 0:
                    return amount
        except (ValueError, OSError):
            pass
    return 0.0


def add_expense():
    raw_date = input("Enter date (YYYY-MM-DD): ").strip()
    try:
        expense_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        if expense_date.isoformat() != raw_date:
            raise ValueError
    except ValueError:
        print("Invalid date. Use YYYY-MM-DD.")
        print("Expense not saved.")
        return

    category = input("Enter category (e.g., Food, Travel): ").strip()
    
    if not category:
        print("Invalid category. Category cannot be empty.")
        return

    amount = get_positive_amount("Enter amount: ")
    if amount is None:
        print("Expense not saved.")
        return

    df = load_expenses()
    new_row = pd.DataFrame([{
        "Date": expense_date.isoformat(),
        "Category": category.title(),
        "Amount": amount
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    save_expenses(df)
    print("Expense saved.")
    show_budget_status(df)

def show_budget_status(df=None):
    if df is None:
        df = load_expenses()
    total = float(df["Amount"].sum()) if not df.empty else 0.0
    remaining = monthly_budget - total
    percentage = (total / monthly_budget * 100) if monthly_budget > 0 else 0.0

    def fmt(x):
        return f"{x:.0f}" if float(x).is_integer() else f"{x:.2f}"
    print(f"Total spent: {fmt(total)} | Remaining: {fmt(remaining)}")

    if monthly_budget <= 0:
        print("Set a monthly budget first using menu option 1.")
    elif percentage > 100:
        print(f"Budget exceeded! ({percentage:.2f}% used)")
    elif total == monthly_budget:
        print("Budget fully used (100.00%).")
    elif percentage >= 80:
        print(f"Warning: {percentage:.2f}% of the budget used.")

def category_summary():
    df = load_expenses()
    if df.empty:
        print("No expenses saved yet.")
        return
    summary = df.groupby("Category", as_index=False)["Amount"].sum()
    
    parts = []
    for _, row in summary.iterrows():
        amount = float(row["Amount"])
        amt_str = f"{amount:.0f}" if amount.is_integer() else f"{amount:.2f}"
        parts.append(f"{row['Category']}: {amt_str}")
        print(" | ".join(parts))

def report():
    df = load_expenses()
    if df.empty:
        print("No expenses saved yet.")
        show_budget_status(df)
        return
    print("\n--- Expense Report ---")
    category_summary()
    show_budget_status(df)

def main():
    global monthly_budget
    monthly_budget = load_budget()
    print("Personal Expenses & Budget Manager")

    while True:
        print("\nMenu")
        print("1. Set budget")
        print("2. Add expense")
        print("3.Category summary")
        print("4. Report")
        print("5. Exit")
        choice = input("Choose an option:").strip()

        if choice == "1":
            set_budget()
        elif choice == "2":
            add_expense()
        elif choice == "3":
            category_summary()
        elif choice == "4":
            report()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid menu option. Choose 1, 2, 3, 4, or 5.")

if __name__ == "__main__":
    main()

