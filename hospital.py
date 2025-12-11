# CREATE DATABASE IF NOT EXISTS hospital_db;
# USE hospital_db;
#
# CREATE TABLE IF NOT EXISTS patients (
#   patient_id INT AUTO_INCREMENT PRIMARY KEY,
#   name VARCHAR(200) NOT NULL,
#   age INT,
#   gender VARCHAR(10),
#   phone VARCHAR(50),
#   address VARCHAR(255),
#   admission_status ENUM('ADMITTED','DISCHARGED') DEFAULT 'DISCHARGED',
#   admitted_at TIMESTAMP NULL DEFAULT NULL,
#   discharged_at TIMESTAMP NULL DEFAULT NULL,
#   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
#
# CREATE TABLE IF NOT EXISTS patient_notes (
#   note_id INT AUTO_INCREMENT PRIMARY KEY,
#   patient_id INT NOT NULL,
#   note TEXT,
#   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#   FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
# );

import mysql.connector
from datetime import datetime

# ---------- CONFIG ----------
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = ""      # change to your password
DB_NAME = "hospital_db"
# ----------------------------

conn = mysql.connector.connect(
    host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
)
cursor = conn.cursor()

def add_patient():
    name = input("Name: ").strip()
    try:
        age = int(input("Age: ").strip())
    except ValueError:
        age = None
    gender = input("Gender: ").strip()
    phone = input("Phone: ").strip()
    address = input("Address: ").strip()
    cursor.execute("""INSERT INTO patients (name,age,gender,phone,address,admission_status) 
                      VALUES (%s,%s,%s,%s,%s,%s)""", (name, age, gender, phone, address, 'DISCHARGED'))
    conn.commit()
    print("Patient added.\n")

def update_patient():
    try:
        pid = int(input("Patient ID to update: ").strip())
    except ValueError:
        print("Invalid id."); return
    name = input("Name (leave blank): ").strip()
    age_in = input("Age (leave blank): ").strip()
    gender = input("Gender (leave blank): ").strip()
    phone = input("Phone (leave blank): ").strip()
    addr = input("Address (leave blank): ").strip()
    parts=[]; vals=[]
    if name: parts.append("name=%s"); vals.append(name)
    if age_in:
        try: parts.append("age=%s"); vals.append(int(age_in))
        except ValueError: print("Invalid age; skipping.")
    if gender: parts.append("gender=%s"); vals.append(gender)
    if phone: parts.append("phone=%s"); vals.append(phone)
    if addr: parts.append("address=%s"); vals.append(addr)
    if not parts:
        print("No changes."); return
    vals.append(pid)
    sql = "UPDATE patients SET " + ",".join(parts) + " WHERE patient_id=%s"
    cursor.execute(sql, tuple(vals)); conn.commit(); print("Updated.\n")

def delete_patient():
    try:
        pid = int(input("Patient ID to delete: ").strip())
    except ValueError:
        print("Invalid id."); return
    confirm = input("Delete patient and notes? (y/n): ").strip().lower()
    if confirm=='y':
        cursor.execute("DELETE FROM patients WHERE patient_id=%s", (pid,))
        conn.commit()
        print("Deleted.\n")
    else:
        print("Cancelled.\n")

def search_patient():
    term = input("Search by name or id: ").strip()
    if term.isdigit():
        cursor.execute("SELECT patient_id,name,age,gender,phone,admission_status FROM patients WHERE patient_id=%s", (int(term),))
    else:
        cursor.execute("SELECT patient_id,name,age,gender,phone,admission_status FROM patients WHERE name LIKE %s", ('%'+term+'%',))
    rows = cursor.fetchall()
    if not rows: print("No results.\n"); return
    for r in rows:
        print(f"ID:{r[0]} Name:{r[1]} Age:{r[2]} Gender:{r[3]} Phone:{r[4]} Status:{r[5]}")
    print()

def view_all_patients():
    cursor.execute("SELECT patient_id,name,age,gender,phone,admission_status,admitted_at,discharged_at FROM patients ORDER BY patient_id")
    rows = cursor.fetchall()
    print("\n--- Patients ---")
    for r in rows:
        print(f"ID:{r[0]} Name:{r[1]} Age:{r[2]} Gender:{r[3]} Phone:{r[4]} Status:{r[5]} Admitted:{r[6]} Discharged:{r[7]}")
    print()

def admit_patient():
    try:
        pid = int(input("Patient ID to admit: ").strip())
    except ValueError:
        print("Invalid id."); return
    cursor.execute("SELECT admission_status FROM patients WHERE patient_id=%s", (pid,))
    r = cursor.fetchone()
    if not r: print("Patient not found."); return
    if r[0]=='ADMITTED':
        print("Already admitted."); return
    cursor.execute("UPDATE patients SET admission_status='ADMITTED', admitted_at=CURRENT_TIMESTAMP, discharged_at=NULL WHERE patient_id=%s", (pid,))
    conn.commit()
    print("Patient admitted.\n")

def discharge_patient():
    try:
        pid = int(input("Patient ID to discharge: ").strip())
    except ValueError:
        print("Invalid id."); return
    cursor.execute("SELECT admission_status FROM patients WHERE patient_id=%s", (pid,))
    r = cursor.fetchone()
    if not r: print("Patient not found."); return
    if r[0]=='DISCHARGED':
        print("Patient already discharged."); return
    cursor.execute("UPDATE patients SET admission_status='DISCHARGED', discharged_at=CURRENT_TIMESTAMP WHERE patient_id=%s", (pid,))
    conn.commit()
    print("Patient discharged.\n")

def add_note():
    try:
        pid = int(input("Patient ID for note: ").strip())
    except ValueError:
        print("Invalid id."); return
    note = input("Enter note: ").strip()
    cursor.execute("INSERT INTO patient_notes (patient_id,note) VALUES (%s,%s)", (pid,note))
    conn.commit()
    print("Note added.\n")

def view_notes():
    try:
        pid = int(input("Patient ID to view notes: ").strip())
    except ValueError:
        print("Invalid id."); return
    cursor.execute("SELECT note_id,note,created_at FROM patient_notes WHERE patient_id=%s ORDER BY created_at DESC", (pid,))
    rows = cursor.fetchall()
    if not rows: print("No notes.\n"); return
    for r in rows:
        print(f"NoteID:{r[0]} At:{r[2]} Note:{r[1]}")
    print()

# ------- MENU -------
def menu():
    while True:
        print("----- Hospital Patient Record System -----")
        print("1. Add Patient")
        print("2. Update Patient")
        print("3. Delete Patient")
        print("4. Search Patient")
        print("5. View All Patients")
        print("6. Admit Patient")
        print("7. Discharge Patient")
        print("8. Add Note")
        print("9. View Notes")
        print("0. Exit")
        ch = input("Enter choice: ").strip()
        if ch=='1': add_patient()
        elif ch=='2': update_patient()
        elif ch=='3': delete_patient()
        elif ch=='4': search_patient()
        elif ch=='5': view_all_patients()
        elif ch=='6': admit_patient()
        elif ch=='7': discharge_patient()
        elif ch=='8': add_note()
        elif ch=='9': view_notes()
        elif ch=='0':
            print("Exiting..."); break
        else:
            print("Invalid choice.\n")

if __name__ == "__main__":
    try:
        menu()
    finally:
        cursor.close(); conn.close()
