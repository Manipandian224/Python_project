import mysql.connector

# -------------------------------
# DATABASE CONNECTION
# -------------------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",        # change if different
        password="",        # add password if set
        database="inventory_db"
    )

# -------------------------------
# ADD PRODUCT
# -------------------------------
def add_product(product_id, name, price, stock):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO products (product_id, name, price, stock_quantity)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (product_id, name, price, stock))
        conn.commit()
        print("✅ Product added successfully")

    except mysql.connector.IntegrityError:
        print("❌ Product ID already exists")

    finally:
        conn.close()

# -------------------------------
# UPDATE STOCK (SALE / RESTOCK)
# -------------------------------
def update_stock(product_id, quantity_change):
    conn = get_connection()
    cursor = conn.cursor()

    # Prevent negative stock
    query = """
    UPDATE products
    SET stock_quantity = stock_quantity + %s
    WHERE product_id = %s
    AND stock_quantity + %s >= 0
    """
    cursor.execute(query, (quantity_change, product_id, quantity_change))
    conn.commit()

    if cursor.rowcount == 0:
        print("❌ Stock update failed (insufficient stock or invalid product)")
    else:
        print("✅ Stock updated successfully")

    conn.close()

# -------------------------------
# LIST LOW STOCK PRODUCTS
# -------------------------------
def list_low_stock(threshold):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT product_id, name, stock_quantity
    FROM products
    WHERE stock_quantity < %s
    """
    cursor.execute(query, (threshold,))

    results = cursor.fetchall()
    print("\n📉 Low Stock Products:")
    for row in results:
        print(row)

    conn.close()

# -------------------------------
# VIEW ALL PRODUCTS
# -------------------------------
def view_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    print("\n📦 Inventory List:")
    for row in rows:
        print(row)

    conn.close()

# -------------------------------
# MAIN PROGRAM
# -------------------------------
if __name__ == "__main__":
    view_products()

    # SALE: reduce stock
    update_stock(102, -2)

    # RESTOCK
    update_stock(103, 5)

    # LOW STOCK CHECK
    list_low_stock(3)

    view_products()
