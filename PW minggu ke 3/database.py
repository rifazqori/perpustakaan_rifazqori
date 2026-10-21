import os

# Driver yang digunakan Flask untuk berkomunikasi dengan PostgreSQL.
import psycopg2


# Password akun PostgreSQL yang dipakai aplikasi.
# Jangan membagikan atau mengunggah file ini selama password tersimpan di sini.
DB_PASSWORD = "rfzqori"


def get_db_connection():
    """Membuka koneksi ke database PostgreSQL aplikasi."""
    return psycopg2.connect(
        # Nilai koneksi dibaca dari environment; nilai setelah koma adalah default.
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ.get("DB_NAME", "flaskDB"),
        user=os.environ.get("DB_USER", "postgres"),
        password=DB_PASSWORD,
    )