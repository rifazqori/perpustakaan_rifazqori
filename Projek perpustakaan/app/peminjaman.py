
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.database import get_db_connection

peminjaman_bp = Blueprint("peminjaman", __name__)


@peminjaman_bp.route("/peminjaman", methods=["GET", "POST"])
def halaman_peminjaman():
    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            if request.method == "POST":
                nama = request.form.get("nama", "").strip()
                email = request.form.get("email", "").strip()
                id_buku = request.form.get("id_buku", type=int)

                if not nama or not email or not id_buku:
                    flash("Semua data wajib diisi.")
                    return redirect(url_for("peminjaman.halaman_peminjaman"))

                cur.execute(
                    "SELECT stok FROM buku WHERE id_buku = %s FOR UPDATE",
                    (id_buku,)
                )
                buku = cur.fetchone()

                if buku is None or buku["stok"] <= 0:
                    conn.rollback()
                    flash("Buku tidak tersedia atau stok habis.")
                    return redirect(url_for("peminjaman.halaman_peminjaman"))

                cur.execute("""
                    INSERT INTO "user" (nama, email)
                    VALUES (%s, %s)
                    ON CONFLICT (email)
                    DO UPDATE SET nama = EXCLUDED.nama
                    RETURNING id_user
                """, (nama, email))
                user = cur.fetchone()

                cur.execute("""
                    INSERT INTO peminjaman (id_user, id_buku)
                    VALUES (%s, %s)
                """, (user["id_user"], id_buku))

                cur.execute("""
                    UPDATE buku
                    SET stok = stok - 1
                    WHERE id_buku = %s
                """, (id_buku,))

                conn.commit()
                flash("Pengajuan peminjaman berhasil disimpan.")
                return redirect(url_for("peminjaman.halaman_peminjaman"))

            cur.execute("""
                SELECT id_buku, judul, stok
                FROM buku
                WHERE stok > 0
                ORDER BY judul
            """)
            daftar_buku = cur.fetchall()

        return render_template(
            "peminjaman.html",
            daftar_buku=daftar_buku
        )
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
