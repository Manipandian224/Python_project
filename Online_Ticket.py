import mysql.connector
import threading
import time
from datetime import datetime, timedelta
import uuid
import random

# ---------------- DATABASE CONNECTION ----------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",          # add password if set
        database="ticket_db"
    )

# ---------------- PAYMENT GATEWAY ----------------
class PaymentGateway:
    @staticmethod
    def process_payment():
        return random.choice([True, False])  # simulate success/failure

# ---------------- RESERVATION MANAGER ----------------
class ReservationManager:
    def __init__(self):
        self.lock = threading.Lock()

    def get_available_seats(self, trip_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT seat_number FROM seats WHERE trip_id=%s AND status='AVAILABLE'",
            (trip_id,)
        )
        seats = cursor.fetchall()
        conn.close()
        return [s[0] for s in seats]

    def reserve_seat(self, trip_id, seat_number, user_id):
        with self.lock:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
            UPDATE seats
            SET status='PENDING', reserved_by=%s, reserved_at=NOW()
            WHERE trip_id=%s AND seat_number=%s AND status='AVAILABLE'
            """
            cursor.execute(query, (user_id, trip_id, seat_number))
            conn.commit()

            if cursor.rowcount == 0:
                conn.close()
                return None, "❌ Seat already taken"

            reservation_id = str(uuid.uuid4())
            conn.close()
            return reservation_id, "✅ Seat reserved (PENDING)"

    def confirm_booking(self, trip_id, seat_number):
        if PaymentGateway.process_payment():
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE seats
                SET status='BOOKED'
                WHERE trip_id=%s AND seat_number=%s AND status='PENDING'
                """,
                (trip_id, seat_number)
            )
            conn.commit()
            conn.close()
            return "✅ Booking confirmed"
        else:
            self.release_seat(trip_id, seat_number)
            return "❌ Payment failed, seat released"

    def release_seat(self, trip_id, seat_number):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE seats
            SET status='AVAILABLE', reserved_by=NULL, reserved_at=NULL
            WHERE trip_id=%s AND seat_number=%s
            """,
            (trip_id, seat_number)
        )
        conn.commit()
        conn.close()

# ---------------- AUTO RELEASE (5 MIN TIMEOUT) ----------------
def auto_release():
    while True:
        time.sleep(30)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE seats
            SET status='AVAILABLE', reserved_by=NULL, reserved_at=NULL
            WHERE status='PENDING'
            AND reserved_at < NOW() - INTERVAL 5 MINUTE
            """
        )
        conn.commit()
        conn.close()

# ---------------- MAIN ----------------
if __name__ == "__main__":
    manager = ReservationManager()

    # Start background timeout thread
    threading.Thread(target=auto_release, daemon=True).start()

    print("Available seats:", manager.get_available_seats("BUS101"))

    reservation_id, msg = manager.reserve_seat("BUS101", 10, "user1")
    print(msg)

    if reservation_id:
        print(manager.confirm_booking("BUS101", 10))
