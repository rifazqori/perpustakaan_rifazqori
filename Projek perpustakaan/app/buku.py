
from flask import Blueprint, render_template
from app.database import get_db_connection

buku_bp = Blueprint("buku", __name__)


@buku_bp.route("/")
def dashboard():
    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    b.id_buku,
                    b.judul,
                    p.nama_penerbit,
                    b.stok
                FROM buku b
                JOIN penerbit p
                    ON b.id_penerbit = p.id_penerbit
                ORDER BY b.judul
            """)
            daftar_buku = cur.fetchall()

        return render_template(
            "buku.html",
            daftar_buku=daftar_buku
        )
    finally:
        conn.close()
