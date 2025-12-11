# CREATE DATABASE IF NOT EXISTS library_db;
# USE library_db;
#
# CREATE TABLE IF NOT EXISTS books (
#   book_id INT AUTO_INCREMENT PRIMARY KEY,
#   title VARCHAR(255) NOT NULL,
#   author VARCHAR(200),
#   isbn VARCHAR(50),
#   copies INT NOT NULL DEFAULT 1,
#   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
#
# CREATE TABLE IF NOT EXISTS users (
#   user_id INT AUTO_INCREMENT PRIMARY KEY,
#   name VARCHAR(200) NOT NULL,
#   email VARCHAR(200),
#   phone VARCHAR(50),
#   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
#
# CREATE TABLE IF NOT EXISTS issued_books (
#   issue_id INT AUTO_INCREMENT PRIMARY KEY,
#   book_id INT NOT NULL,
#   user_id INT NOT NULL,
#   issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#   returned_at TIMESTAMP NULL DEFAULT NULL,
#   FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
#   FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
# );


import mysql.connector

# ---------- CONFIG ----------
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = ""      # change to your password
DB_NAME = "library_db"
# ----------------------------

conn = mysql.connector.connect(
    host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
)
cursor = conn.cursor()

# ------- BOOKS -------
def add_book():
    title = input("Title: ").strip()
    author = input("Author: ").strip()
    isbn = input("ISBN: ").strip()
    try:
        copies = int(input("Copies: ").strip())
    except ValueError:
        print("Invalid copies. Using 1.")
        copies = 1
    sql = "INSERT INTO books (title, author, isbn, copies) VALUES (%s,%s,%s,%s)"
    cursor.execute(sql, (title, author, isbn, copies))
    conn.commit()
    print("Book added.\n")

def update_book():
    try:
        bid = int(input("Book ID to update: ").strip())
    except ValueError:
        print("Invalid ID."); return
    title = input("New title: ").strip()
    author = input("New author: ").strip()
    isbn = input("New ISBN: ").strip()
    try:
        copies = int(input("New copies: ").strip())
    except ValueError:
        copies = None
    parts = []
    vals = []
    if title: parts.append("title=%s"); vals.append(title)
    if author: parts.append("author=%s"); vals.append(author)
    if isbn: parts.append("isbn=%s"); vals.append(isbn)
    if copies is not None: parts.append("copies=%s"); vals.append(copies)
    if not parts:
        print("No changes.")
        return
    sql = "UPDATE books SET " + ",".join(parts) + " WHERE book_id=%s"
    vals.append(bid)
    cursor.execute(sql, tuple(vals))
    conn.commit()
    print("Book updated.\n")

def delete_book():
    try:
        bid = int(input("Book ID to delete: ").strip())
    except ValueError:
        print("Invalid ID."); return
    cursor.execute("DELETE FROM books WHERE book_id=%s", (bid,))
    conn.commit()
    print("Book deleted.\n")

def list_books():
    cursor.execute("SELECT book_id,title,author,isbn,copies FROM books ORDER BY book_id")
    rows = cursor.fetchall()
    print("\n--- Books ---")
    for r in rows:
        print(f"ID:{r[0]} Title:{r[1]} Author:{r[2]} ISBN:{r[3]} Copies:{r[4]}")
    print()

# ------- USERS -------
def register_user():
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()
    cursor.execute("INSERT INTO users (name,email,phone) VALUES (%s,%s,%s)", (name,email,phone))
    conn.commit()
    print("User registered.\n")

def list_users():
    cursor.execute("SELECT user_id,name,email,phone FROM users ORDER BY user_id")
    rows = cursor.fetchall()
    print("\n--- Users ---")
    for r in rows:
        print(f"ID:{r[0]} Name:{r[1]} Email:{r[2]} Phone:{r[3]}")
    print()

# ------- ISSUE / RETURN -------
def issue_book():
    try:
        book_id = int(input("Book ID to issue: ").strip())
        user_id = int(input("User ID: ").strip())
    except ValueError:
        print("Invalid id."); return

    # check copies available
    cursor.execute("SELECT copies FROM books WHERE book_id=%s", (book_id,))
    row = cursor.fetchone()
    if not row:
        print("Book not found."); return
    if row[0] < 1:
        print("No copies available."); return

    cursor.execute("INSERT INTO issued_books (book_id,user_id) VALUES (%s,%s)", (book_id,user_id))
    cursor.execute("UPDATE books SET copies = copies - 1 WHERE book_id=%s", (book_id,))
    conn.commit()
    print("Book issued.\n")

def return_book():
    try:
        issue_id = int(input("Issue ID to return: ").strip())
    except ValueError:
        print("Invalid id."); return
    cursor.execute("SELECT book_id, returned_at FROM issued_books WHERE issue_id=%s", (issue_id,))
    r = cursor.fetchone()
    if not r:
        print("Issue record not found."); return
    if r[1] is not None:
        print("Already returned."); return
    book_id = r[0]
    cursor.execute("UPDATE issued_books SET returned_at=CURRENT_TIMESTAMP WHERE issue_id=%s", (issue_id,))
    cursor.execute("UPDATE books SET copies = copies + 1 WHERE book_id=%s", (book_id,))
    conn.commit()
    print("Book returned.\n")

def view_issued():
    cursor.execute("""SELECT i.issue_id, b.title, u.name, i.issued_at, i.returned_at
                      FROM issued_books i
                      JOIN books b ON i.book_id=b.book_id
                      JOIN users u ON i.user_id=u.user_id
                      ORDER BY i.issue_id DESC""")
    rows = cursor.fetchall()
    print("\n--- Issued Books ---")
    for r in rows:
        print(f"IssueID:{r[0]} Book:{r[1]} User:{r[2]} Issued:{r[3]} Returned:{r[4]}")
    print()

# ------- SEARCH -------
def search_books():
    term = input("Search by title/author/ISBN: ").strip()
    q = "%" + term + "%"
    cursor.execute("SELECT book_id,title,author,isbn,copies FROM books WHERE title LIKE %s OR author LIKE %s OR isbn LIKE %s", (q,q,q))
    rows = cursor.fetchall()
    if not rows: print("No results.\n"); return
    for r in rows:
        print(f"ID:{r[0]} Title:{r[1]} Author:{r[2]} ISBN:{r[3]} Copies:{r[4]}")
    print()

# ------- MENU -------
def menu():
    while True:
        print("----- Library Management -----")
        print("1. Add Book")
        print("2. Update Book")
        print("3. Delete Book")
        print("4. List Books")
        print("5. Register User")
        print("6. List Users")
        print("7. Issue Book")
        print("8. Return Book")
        print("9. View Issued Books")
        print("10. Search Books")
        print("0. Exit")
        choice = input("Enter choice: ").strip()
        if choice=='1': add_book()
        elif choice=='2': update_book()
        elif choice=='3': delete_book()
        elif choice=='4': list_books()
        elif choice=='5': register_user()
        elif choice=='6': list_users()
        elif choice=='7': issue_book()
        elif choice=='8': return_book()
        elif choice=='9': view_issued()
        elif choice=='10': search_books()
        elif choice=='0':
            print("Exiting..."); break
        else:
            print("Invalid choice.\n")

if __name__ == "__main__":
    try:
        menu()
    finally:
        cursor.close(); conn.close()
