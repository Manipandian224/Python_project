import mysql.connector
import string
import random
import hashlib

BASE_URL = "http://short.url/"

# ---------------- DATABASE CONNECTION ----------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",          # add password if set
        database="url_shortener_db"
    )

# ---------------- URLMap CLASS ----------------
class URLMap:
    @staticmethod
    def save(short_id, long_url):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO url_map (short_id, long_url) VALUES (%s, %s)",
            (short_id, long_url)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get(short_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT long_url FROM url_map WHERE short_id=%s",
            (short_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    @staticmethod
    def increment_click(short_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE url_map SET click_count = click_count + 1 WHERE short_id=%s",
            (short_id,)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_click_count(short_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT click_count FROM url_map WHERE short_id=%s",
            (short_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0

    @staticmethod
    def exists(short_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM url_map WHERE short_id=%s",
            (short_id,)
        )
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

# ---------------- SHORTENER SERVICE ----------------
class ShortenerService:

    @staticmethod
    def generate_short_id(long_url):
        # Hash + base conversion (7 chars)
        hash_val = hashlib.md5(long_url.encode()).hexdigest()
        return hash_val[:7]

    @staticmethod
    def shorten_url(long_url, desired_alias=None):
        if desired_alias:
            if URLMap.exists(desired_alias):
                return "❌ Alias already exists"
            short_id = desired_alias
        else:
            while True:
                short_id = ShortenerService.generate_short_id(
                    long_url + str(random.randint(1, 10000))
                )
                if not URLMap.exists(short_id):
                    break

        URLMap.save(short_id, long_url)
        return BASE_URL + short_id

    @staticmethod
    def get_long_url(short_id):
        long_url = URLMap.get(short_id)
        if not long_url:
            return "❌ Short URL not found"

        URLMap.increment_click(short_id)
        return long_url

    @staticmethod
    def get_click_count(short_id):
        return URLMap.get_click_count(short_id)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    short_url = ShortenerService.shorten_url(
        "https://www.google.com/search?q=python+url+shortener"
    )
    print("Short URL:", short_url)

    sid = short_url.split("/")[-1]
    print("Redirect to:", ShortenerService.get_long_url(sid))
    print("Click Count:", ShortenerService.get_click_count(sid))
