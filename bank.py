# CREATE TABLE IF NOT EXISTS accounts (
#   account_id INT AUTO_INCREMENT PRIMARY KEY,
#   account_number VARCHAR(20) NOT NULL UNIQUE,
#   name VARCHAR(100) NOT NULL,
#   balance DECIMAL(12,2) NOT NULL DEFAULT 0.00,
#   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
# CREATE TABLE IF NOT EXISTS transactions (
#   transaction_id INT AUTO_INCREMENT PRIMARY KEY,
#   account_id INT NOT NULL,
#   type ENUM('DEPOSIT','WITHDRAW','TRANSFER_IN','TRANSFER_OUT') NOT NULL,
#   amount DECIMAL(12,2) NOT NULL,
#   balance_after DECIMAL(12,2) NOT NULL,
#   note VARCHAR(255),
#   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#   FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
# );
import mysql.connector
from mysql.connector import Error
import sys
import random
import string

# ---------- CONFIG ----------
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = ""      # change to your password
DB_NAME = "bank_db"
# ----------------------------

# Connect (assumes DB and tables created). If not, create tables beforehand using SQL above.
conn = mysql.connector.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = conn.cursor()

# ---------- Utility ----------
def generate_account_number(length=10):
    # simple random numeric account number (ensure uniqueness when inserting)
    return ''.join(random.choices(string.digits, k=length))


def get_account_by_number(acc_no):
    cursor.execute("SELECT account_id, account_number, name, balance FROM accounts WHERE account_number = %s", (acc_no,))
    return cursor.fetchone()  # None or tuple


def get_account_by_id(aid):
    cursor.execute("SELECT account_id, account_number, name, balance FROM accounts WHERE account_id = %s", (aid,))
    return cursor.fetchone()


def create_transaction(account_id, ttype, amount, balance_after, note=None):
    sql = "INSERT INTO transactions (account_id, type, amount, balance_after, note) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, (account_id, ttype, amount, balance_after, note))
    conn.commit()


# ---------- FEATURES ----------
def create_account():
    name = input("Enter account holder name: ").strip()
    # initial deposit optional
    try:
        init = input("Initial deposit amount (leave blank for 0): ").strip()
        init_amount = float(init) if init != "" else 0.0
    except ValueError:
        print("Invalid amount. Aborting.")
        return

    # Try to generate unique account number
    for _ in range(5):
        acc_no = generate_account_number()
        cursor.execute("SELECT 1 FROM accounts WHERE account_number=%s", (acc_no,))
        if not cursor.fetchone():
            break
    else:
        print("Could not generate unique account number. Try again.")
        return

    sql = "INSERT INTO accounts (account_number, name, balance) VALUES (%s, %s, %s)"
    cursor.execute(sql, (acc_no, name, round(init_amount, 2)))
    conn.commit()
    account_id = cursor.lastrowid
    if init_amount > 0:
        create_transaction(account_id, "DEPOSIT", round(init_amount, 2), round(init_amount, 2), "Initial deposit")
    print(f"\nAccount created: {acc_no} (ID: {account_id}) with balance {init_amount:.2f}\n")


def delete_account():
    acc_no = input("Enter account number to delete: ").strip()
    acct = get_account_by_number(acc_no)
    if not acct:
        print("Account not found.")
        return
    confirm = input(f"Are you sure you want to delete account {acc_no} (holder: {acct[2]})? This deletes transactions too. (y/n): ").lower()
    if confirm == "y":
        cursor.execute("DELETE FROM accounts WHERE account_number=%s", (acc_no,))
        conn.commit()
        print("Account deleted.\n")
    else:
        print("Cancelled.\n")


def deposit():
    acc_no = input("Enter account number: ").strip()
    acct = get_account_by_number(acc_no)
    if not acct:
        print("Account not found.")
        return
    try:
        amt = float(input("Enter deposit amount: "))
        if amt <= 0:
            print("Amount must be positive.")
            return
    except ValueError:
        print("Invalid amount.")
        return

    new_balance = float(acct[3]) + round(amt, 2)
    cursor.execute("UPDATE accounts SET balance=%s WHERE account_id=%s", (new_balance, acct[0]))
    conn.commit()
    create_transaction(acct[0], "DEPOSIT", round(amt, 2), round(new_balance, 2), "Deposit")
    print(f"Deposited {amt:.2f}. New balance: {new_balance:.2f}\n")


def withdraw():
    acc_no = input("Enter account number: ").strip()
    acct = get_account_by_number(acc_no)
    if not acct:
        print("Account not found.")
        return
    try:
        amt = float(input("Enter withdrawal amount: "))
        if amt <= 0:
            print("Amount must be positive.")
            return
    except ValueError:
        print("Invalid amount.")
        return

    if float(acct[3]) < amt:
        print("Insufficient funds.")
        return

    new_balance = float(acct[3]) - round(amt, 2)
    cursor.execute("UPDATE accounts SET balance=%s WHERE account_id=%s", (new_balance, acct[0]))
    conn.commit()
    create_transaction(acct[0], "WITHDRAW", round(amt, 2), round(new_balance, 2), "Withdrawal")
    print(f"Withdrawn {amt:.2f}. New balance: {new_balance:.2f}\n")


def transfer():
    from_acc = input("From account number: ").strip()
    to_acc = input("To account number: ").strip()
    if from_acc == to_acc:
        print("Cannot transfer to the same account.")
        return
    from_acct = get_account_by_number(from_acc)
    to_acct = get_account_by_number(to_acc)
    if not from_acct or not to_acct:
        print("One or both accounts not found.")
        return
    try:
        amt = float(input("Enter transfer amount: "))
        if amt <= 0:
            print("Amount must be positive.")
            return
    except ValueError:
        print("Invalid amount.")
        return
    if float(from_acct[3]) < amt:
        print("Insufficient funds in source account.")
        return

    # perform transfer in a simple transaction (two updates + two transaction records)
    try:
        # subtract from source
        new_from_balance = float(from_acct[3]) - round(amt, 2)
        # add to destination
        new_to_balance = float(to_acct[3]) + round(amt, 2)

        cursor.execute("UPDATE accounts SET balance=%s WHERE account_id=%s", (new_from_balance, from_acct[0]))
        cursor.execute("UPDATE accounts SET balance=%s WHERE account_id=%s", (new_to_balance, to_acct[0]))

        # record transactions
        create_transaction(from_acct[0], "TRANSFER_OUT", round(amt, 2), round(new_from_balance, 2), f"To {to_acc}")
        create_transaction(to_acct[0], "TRANSFER_IN", round(amt, 2), round(new_to_balance, 2), f"From {from_acc}")

        print(f"Transferred {amt:.2f} from {from_acc} to {to_acc}.\n")
    except Error as e:
        conn.rollback()
        print("Transfer failed:", e)


def view_balance():
    acc_no = input("Enter account number: ").strip()
    acct = get_account_by_number(acc_no)
    if not acct:
        print("Account not found.")
        return
    print(f"Account: {acct[1]}  Holder: {acct[2]}  Balance: {float(acct[3]):.2f}\n")


def account_transactions():
    acc_no = input("Enter account number to view transactions: ").strip()
    acct = get_account_by_number(acc_no)
    if not acct:
        print("Account not found.")
        return
    cursor.execute("SELECT transaction_id, type, amount, balance_after, note, created_at FROM transactions WHERE account_id=%s ORDER BY created_at DESC", (acct[0],))
    rows = cursor.fetchall()
    if not rows:
        print("No transactions found.\n")
        return
    print(f"\n--- Transactions for {acc_no} ({acct[2]}) ---")
    for r in rows:
        print(f"ID:{r[0]}  {r[1]}  Amount:{float(r[2]):.2f}  BalAfter:{float(r[3]):.2f}  Note:{r[4]}  At:{r[5]}")
    print()


def list_accounts():
    cursor.execute("SELECT account_number, name, balance, created_at FROM accounts ORDER BY account_id")
    rows = cursor.fetchall()
    if not rows:
        print("No accounts.\n")
        return
    print("\n--- Accounts ---")
    for r in rows:
        print(f"Acc:{r[0]}  Name:{r[1]}  Bal:{float(r[2]):.2f}  Created:{r[3]}")
    print()


def search_accounts():
    term = input("Enter name or account number to search: ").strip()
    q = "%" + term + "%"
    cursor.execute("SELECT account_number, name, balance FROM accounts WHERE name LIKE %s OR account_number LIKE %s", (q, q))
    rows = cursor.fetchall()
    if not rows:
        print("No results.\n")
        return
    print("\n--- Search Results ---")
    for r in rows:
        print(f"Acc:{r[0]}  Name:{r[1]}  Bal:{float(r[2]):.2f}")
    print()


# ---------- Menu ----------
def menu():
    while True:
        print("----- Simple Banking System -----")
        print("1. Create Account")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer")
        print("5. View Balance")
        print("6. View Transactions")
        print("7. List Accounts")
        print("8. Search Accounts")
        print("9. Delete Account")
        print("0. Exit")

        choice = input("Enter choice: ").strip()
        if choice == '1':
            create_account()
        elif choice == '2':
            deposit()
        elif choice == '3':
            withdraw()
        elif choice == '4':
            transfer()
        elif choice == '5':
            view_balance()
        elif choice == '6':
            account_transactions()
        elif choice == '7':
            list_accounts()
        elif choice == '8':
            search_accounts()
        elif choice == '9':
            delete_account()
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.\n")


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
    finally:
        cursor.close()
        conn.close()
