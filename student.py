# Database: `students_db`
# -- Table structure for table `students`
# --
#
# CREATE TABLE `students` (
#   `student_id` int(11) NOT NULL,
#   `name` varchar(100) NOT NULL,
#   `age` int(11) NOT NULL,
#   `student_class` varchar(20) NOT NULL,
#   `marks` float NOT NULL
# )


import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    port=3306,# your MySQL username
    password="",       # your MySQL password
    database="students_db"
)

cursor = conn.cursor()

def add_student():
    name = input("Enter student name: ")
    age = int(input("Enter age: "))
    student_class = input("Enter class: ")
    marks = float(input("Enter marks: "))
    sql = "INSERT INTO students (name, age, student_class, marks) VALUES (%s, %s, %s, %s)"
    val = (name, age, student_class, marks)
    cursor.execute(sql, val)
    conn.commit()
    print("Student added successfully!\n")

def view_students():
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    print("\n--- Student List ---")
    for student in students:
        print(f"ID: {student[0]}, Name: {student[1]}, Age: {student[2]}, Class: {student[3]}, Marks: {student[4]}")
    print()

def update_student():
    student_id = int(input("Enter student ID to update: "))
    print("Enter new details:")
    name = input("Name: ")
    age = int(input("Age: "))
    student_class = input("Class: ")
    marks = float(input("Marks: "))
    sql = "UPDATE students SET name=%s, age=%s, student_class=%s, marks=%s WHERE student_id=%s"
    val = (name, age, student_class, marks, student_id)
    cursor.execute(sql, val)
    conn.commit()
    print("Student updated successfully!\n")

def delete_student():
    student_id = int(input("Enter student ID to delete: "))
    sql = "DELETE FROM students WHERE student_id=%s"
    cursor.execute(sql, (student_id,))
    conn.commit()
    print("Student deleted successfully!\n")

def search_student():
    name = input("Enter student name to search: ")
    sql = "SELECT * FROM students WHERE name LIKE %s"
    cursor.execute(sql, ('%' + name + '%',))
    students = cursor.fetchall()
    print("\n--- Search Results ---")
    for student in students:
        print(f"ID: {student[0]}, Name: {student[1]}, Age: {student[2]}, Class: {student[3]}, Marks: {student[4]}")
    print()

def menu():
    while True:
        print("----- Student Management System -----")
        print("1. Add Student")
        print("2. View All Students")
        print("3. Update Student")
        print("4. Delete Student")
        print("5. Search Student")
        print("6. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            add_student()
        elif choice == '2':
            view_students()
        elif choice == '3':
            update_student()
        elif choice == '4':
            delete_student()
        elif choice == '5':
            search_student()
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice! Try again.\n")

if __name__ == "__main__":
    menu()
    cursor.close()
    conn.close()
