import sqlite3
import os
import shutil
from datetime import datetime

DB_NAME = "finance_app.db"

# ============ DATABASE SETUP ============
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )''')

    # Transactions table
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        type TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES users(username)
    )''')

    # Budget table
    cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
        username TEXT PRIMARY KEY,
        amount REAL NOT NULL,
        FOREIGN KEY (username) REFERENCES users(username)
    )''')

    conn.commit()
    conn.close()

# ============ USER AUTH ============
def register():
    username = input("Enter new username: ")
    password = input("Enter new password: ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        conn.commit()
        print("✅ Registration successful!")
    except sqlite3.IntegrityError:
        print("❌ Username already exists.")
    conn.close()

def login():
    username = input("Username: ")
    password = input("Password: ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        print("✅ Login successful!")
        return username
    else:
        print("❌ Invalid credentials.")
        return None

# ============ TRANSACTION MANAGEMENT ============
def add_transaction(username):
    t_type = input("Enter type (income/expense): ").lower()
    category = input("Enter category: ")
    amount = float(input("Enter amount: "))
    date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (username, type, category, amount, date) VALUES (?, ?, ?, ?, ?)",
                   (username, t_type, category, amount, date))
    conn.commit()
    conn.close()
    print("✅ Transaction added successfully.")

def view_transactions(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE username=?", (username,))
    rows = cursor.fetchall()
    conn.close()

    if rows:
        print("\n📜 Transactions:")
        for row in rows:
            print(row)
    else:
        print("No transactions found.")

# ============ REPORTS ============
def generate_report(username):
    year = input("Enter year (YYYY): ")
    month = input("Enter month (MM or leave blank for yearly): ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if month:
        cursor.execute("""SELECT type, SUM(amount) 
                          FROM transactions 
                          WHERE username=? AND strftime('%Y', date)=? AND strftime('%m', date)=?
                          GROUP BY type""", (username, year, month))
    else:
        cursor.execute("""SELECT type, SUM(amount) 
                          FROM transactions 
                          WHERE username=? AND strftime('%Y', date)=?
                          GROUP BY type""", (username, year))

    data = cursor.fetchall()
    conn.close()

    total_income = sum(amount for t_type, amount in data if t_type == 'income')
    total_expense = sum(amount for t_type, amount in data if t_type == 'expense')
    savings = total_income - total_expense

    print(f"\n📊 Report for {month+'/'+year if month else year}")
    print(f"Total Income: ₹{total_income}")
    print(f"Total Expenses: ₹{total_expense}")
    print(f"Savings: ₹{savings}")

# ============ BUDGET ============
def set_budget(username):
    amount = float(input("Enter your monthly budget: "))
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO budgets (username, amount) VALUES (?, ?)", (username, amount))
    conn.commit()
    conn.close()
    print("✅ Budget set successfully.")

def check_budget(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT amount FROM budgets WHERE username=?", (username,))
    budget = cursor.fetchone()

    cursor.execute("""SELECT SUM(amount) FROM transactions 
                      WHERE username=? AND type='expense' AND strftime('%Y-%m', date)=strftime('%Y-%m', 'now')""",
                   (username,))
    total_expenses = cursor.fetchone()[0] or 0
    conn.close()

    if budget:
        print(f"💰 Monthly Budget: ₹{budget[0]}, Spent: ₹{total_expenses}")
        if total_expenses > budget[0]:
            print("⚠️ You have exceeded your budget!")
    else:
        print("No budget set.")

# ============ BACKUP / RESTORE ============
def backup_db():
    backup_file = "finance_backup.db"
    shutil.copy(DB_NAME, backup_file)
    print(f"✅ Backup created as {backup_file}")

def restore_db():
    backup_file = input("Enter backup file name to restore from: ")
    if os.path.exists(backup_file):
        shutil.copy(backup_file, DB_NAME)
        print("✅ Database restored successfully.")
    else:
        print("❌ Backup file not found.")

# ============ MAIN MENU ============
def main():
    init_db()
    print("📌 Personal Finance Manager")

    while True:
        choice = input("\n1. Register\n2. Login\n3. Exit\nChoose: ")
        if choice == '1':
            register()
        elif choice == '2':
            username = login()
            if username:
                while True:
                    user_choice = input("\n1. Add Transaction\n2. View Transactions\n3. Generate Report\n4. Set Budget\n5. Check Budget\n6. Backup Data\n7. Restore Data\n8. Logout\nChoose: ")
                    if user_choice == '1':
                        add_transaction(username)
                    elif user_choice == '2':
                        view_transactions(username)
                    elif user_choice == '3':
                        generate_report(username)
                    elif user_choice == '4':
                        set_budget(username)
                    elif user_choice == '5':
                        check_budget(username)
                    elif user_choice == '6':
                        backup_db()
                    elif user_choice == '7':
                        restore_db()
                    elif user_choice == '8':
                        break
        elif choice == '3':
            break

if __name__ == "__main__":
    main()
