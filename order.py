import mysql.connector

# ---------- CONFIG ----------
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = ""      # change to your password
DB_NAME = "orders_db"
# ----------------------------

conn = mysql.connector.connect(
    host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
)
cursor = conn.cursor()

# ------- MENU ITEMS -------
def add_menu_item():
    name = input("Item name: ").strip()
    try:
        price = float(input("Price: ").strip())
    except ValueError:
        print("Invalid price."); return
    cursor.execute("INSERT INTO menu_items (name,price) VALUES (%s,%s)", (name,price))
    conn.commit()
    print("Menu item added.\n")

def list_menu():
    cursor.execute("SELECT item_id,name,price,available FROM menu_items ORDER BY item_id")
    rows = cursor.fetchall()
    print("\n--- Menu ---")
    for r in rows:
        print(f"ID:{r[0]} Name:{r[1]} Price:{float(r[2]):.2f} Available:{bool(r[3])}")
    print()

def update_menu_item():
    try:
        iid = int(input("Item ID to update: ").strip())
    except ValueError:
        print("Invalid id."); return
    name = input("New name (leave blank): ").strip()
    price_in = input("New price (leave blank): ").strip()
    avail_in = input("Available? (y/n/leave blank): ").strip().lower()
    parts=[]; vals=[]
    if name: parts.append("name=%s"); vals.append(name)
    if price_in:
        try: p=float(price_in); parts.append("price=%s"); vals.append(p)
        except ValueError: print("Invalid price; skipping.")
    if avail_in in ("y","n"):
        parts.append("available=%s"); vals.append(1 if avail_in=="y" else 0)
    if not parts:
        print("No changes."); return
    vals.append(iid)
    sql = "UPDATE menu_items SET " + ",".join(parts) + " WHERE item_id=%s"
    cursor.execute(sql, tuple(vals)); conn.commit(); print("Updated.\n")

# ------- ORDERS -------
def place_order():
    customer = input("Customer name: ").strip()
    items = []
    while True:
        try:
            iid = input("Enter menu item id (blank to finish): ").strip()
            if iid == "": break
            iid = int(iid)
            qty = int(input("Qty: ").strip())
            items.append((iid, qty))
        except ValueError:
            print("Invalid input; try again.")
    if not items:
        print("No items. Order cancelled."); return
    # calculate total and check availability
    total = 0.0
    order_items = []
    for iid, qty in items:
        cursor.execute("SELECT name,price,available FROM menu_items WHERE item_id=%s", (iid,))
        r = cursor.fetchone()
        if not r:
            print(f"Item id {iid} not found. Aborting."); return
        if not r[2]:
            print(f"Item {r[0]} not available. Aborting."); return
        price = float(r[1])
        total += price * qty
        order_items.append((iid, qty, price))
    # insert order
    cursor.execute("INSERT INTO orders (customer_name,total,payment_status) VALUES (%s,%s,%s)", (customer, round(total,2), "PENDING"))
    order_id = cursor.lastrowid
    for iid, qty, price in order_items:
        cursor.execute("INSERT INTO order_items (order_id,item_id,qty,price) VALUES (%s,%s,%s,%s)", (order_id,iid,qty,price))
    conn.commit()
    print(f"Order placed. Order ID: {order_id} Total: {total:.2f} Status: PENDING\n")

def list_orders():
    cursor.execute("SELECT order_id,customer_name,total,payment_status,created_at FROM orders ORDER BY order_id DESC")
    rows = cursor.fetchall()
    print("\n--- Orders ---")
    for r in rows:
        print(f"ID:{r[0]} Customer:{r[1]} Total:{float(r[2]):.2f} Status:{r[3]} At:{r[4]}")
    print()

def view_order_items():
    try:
        oid = int(input("Order ID: ").strip())
    except ValueError:
        print("Invalid id."); return
    cursor.execute("""SELECT oi.id, m.name, oi.qty, oi.price
                      FROM order_items oi JOIN menu_items m ON oi.item_id=m.item_id
                      WHERE oi.order_id=%s""", (oid,))
    rows = cursor.fetchall()
    if not rows:
        print("No items or order not found.\n"); return
    print(f"\n--- Items for Order {oid} ---")
    for r in rows:
        print(f"LineID:{r[0]} Item:{r[1]} Qty:{r[2]} Price:{float(r[3]):.2f}")
    print()

def update_payment_status():
    try:
        oid = int(input("Order ID: ").strip())
    except ValueError:
        print("Invalid id."); return
    status = input("New status (PENDING/PAID/CANCELLED): ").strip().upper()
    if status not in ("PENDING","PAID","CANCELLED"):
        print("Invalid status."); return
    cursor.execute("UPDATE orders SET payment_status=%s WHERE order_id=%s", (status,oid))
    conn.commit()
    print("Order status updated.\n")

def order_history_by_customer():
    name = input("Customer name to lookup: ").strip()
    cursor.execute("SELECT order_id,total,payment_status,created_at FROM orders WHERE customer_name LIKE %s ORDER BY created_at DESC", ('%'+name+'%',))
    rows = cursor.fetchall()
    if not rows: print("No orders.\n"); return
    for r in rows:
        print(f"Order:{r[0]} Total:{float(r[1]):.2f} Status:{r[2]} At:{r[3]}")
    print()

# ------- MENU -------
def menu():
    while True:
        print("----- Online Order System -----")
        print("1. Add Menu Item")
        print("2. List Menu")
        print("3. Update Menu Item")
        print("4. Place Order")
        print("5. List Orders")
        print("6. View Order Items")
        print("7. Update Payment Status")
        print("8. Order History by Customer")
        print("0. Exit")
        c = input("Enter choice: ").strip()
        if c=='1': add_menu_item()
        elif c=='2': list_menu()
        elif c=='3': update_menu_item()
        elif c=='4': place_order()
        elif c=='5': list_orders()
        elif c=='6': view_order_items()
        elif c=='7': update_payment_status()
        elif c=='8': order_history_by_customer()
        elif c=='0':
            print("Exiting..."); break
        else:
            print("Invalid choice.\n")

if __name__ == "__main__":
    try:
        menu()
    finally:
        cursor.close(); conn.close()
