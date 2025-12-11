import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",      # your MySQL password
    port=3306,        # change if needed
    database="inventory_db"
)

cursor = conn.cursor()

# ------------------------------
# ADD PRODUCT
# ------------------------------
def add_product():
    name = input("Enter product name: ")
    price = float(input("Enter price: "))
    quantity = int(input("Enter quantity: "))
    description = input("Enter description: ")

    sql = "INSERT INTO products (name, price, quantity, description) VALUES (%s, %s, %s, %s)"
    val = (name, price, quantity, description)

    cursor.execute(sql, val)
    conn.commit()
    print("\nProduct added successfully!\n")


# ------------------------------
# VIEW PRODUCTS
# ------------------------------
def view_products():
    cursor.execute("SELECT * FROM products")
    records = cursor.fetchall()

    print("\n--- Product List ---")
    for p in records:
        print(f"ID: {p[0]}, Name: {p[1]}, Price: {p[2]}, Qty: {p[3]}, Desc: {p[4]}")
    print()


# ------------------------------
# UPDATE PRODUCT
# ------------------------------
def update_product():
    product_id = int(input("Enter product ID to update: "))

    print("Enter new details:")
    name = input("Name: ")
    price = float(input("Price: "))
    quantity = int(input("Quantity: "))
    description = input("Description: ")

    sql = """
    UPDATE products 
    SET name=%s, price=%s, quantity=%s, description=%s 
    WHERE product_id=%s
    """

    val = (name, price, quantity, description, product_id)

    cursor.execute(sql, val)
    conn.commit()
    print("\nProduct updated successfully!\n")


# ------------------------------
# DELETE PRODUCT
# ------------------------------
def delete_product():
    product_id = int(input("Enter product ID to delete: "))

    sql = "DELETE FROM products WHERE product_id=%s"
    cursor.execute(sql, (product_id,))

    conn.commit()
    print("\nProduct deleted successfully!\n")


# ------------------------------
# SEARCH PRODUCT
# ------------------------------
def search_product():
    name = input("Enter product name to search: ")

    sql = "SELECT * FROM products WHERE name LIKE %s"
    cursor.execute(sql, ('%' + name + '%',))

    records = cursor.fetchall()

    print("\n--- Search Results ---")
    for p in records:
        print(f"ID: {p[0]}, Name: {p[1]}, Price: {p[2]}, Qty: {p[3]}, Desc: {p[4]}")
    print()


# ------------------------------
# MENU SYSTEM
# ------------------------------
def menu():
    while True:
        print("----- Inventory Management System -----")
        print("1. Add Product")
        print("2. View All Products")
        print("3. Update Product")
        print("4. Delete Product")
        print("5. Search Product")
        print("6. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            add_product()
        elif choice == '2':
            view_products()
        elif choice == '3':
            update_product()
        elif choice == '4':
            delete_product()
        elif choice == '5':
            search_product()
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice! Try again.\n")


# ------------------------------
# MAIN
# ------------------------------
if __name__ == "__main__":
    menu()
    cursor.close()
    conn.close()
