# Mengimpor Flask dan render_template
from flask import Flask, render_template

# Mengimpor fungsi untuk membuka koneksi ke PostgreSQL
from database import get_db_connection


# Membuat objek aplikasi yang akan mengatur URL dan halaman web
app = Flask(__name__)


# URL "/" akan menampilkan daftar data dari tabel admin
@app.route("/")
def home():
    # Membuka koneksi dan cursor; keduanya ditutup otomatis setelah blok selesai
    with get_db_connection() as connection:
        with connection.cursor() as cur:
            # Mengambil semua baris dari tabel admin
            cur.execute("SELECT * FROM admin")
            # Menyimpan hasil query agar bisa dikirim ke template
            data = cur.fetchall()

    # Mengirim data ke home.html dengan nama "users"
    return render_template("home.html", users=data)


# URL "/about" menampilkan halaman informasi tanpa mengambil data database
@app.route("/about")
def about():
    return render_template("about.html")


# URL "/admin" juga menampilkan daftar baris dari tabel admin
@app.route("/admin")
def admin():
    with get_db_connection() as connection:
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM admin")
            data = cur.fetchall()

    # Menggunakan template dan nama variabel yang sama dengan halaman utama
    return render_template("home.html", users=data)


if __name__ == "__main__":
    # Menjalankan server pengembangan Flask; debug=True untuk penggunaan lokal
    app.run(debug=True)