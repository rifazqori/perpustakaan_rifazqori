from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from app.database import get_db_connection

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "admin_id" not in session:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)
    return wrapped


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if "admin_id" in session:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id_admin, username, password_hash FROM admin WHERE username = %s",
                    (username,)
                )
                admin = cur.fetchone()
        finally:
            conn.close()

        if admin and check_password_hash(admin["password_hash"], password):
            session.clear()
            session["admin_id"] = admin["id_admin"]
            session["admin_username"] = admin["username"]
            return redirect(url_for("admin.dashboard"))

        flash("Username atau password salah.", "danger")

    return render_template("admin_login.html")


@admin_bp.route("/logout", methods=["POST"])
@admin_required
def logout():
    session.clear()
    flash("Berhasil logout.", "success")
    return redirect(url_for("admin.login"))



@admin_bp.route("/")
@admin_required
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
            "admin_dashboard.html",
            daftar_buku=daftar_buku
        )
    finally:
        conn.close()



@admin_bp.route("/buku/tambah", methods=["GET", "POST"])
@admin_required
def tambah_buku():
    conn = get_db_connection()

    try:
        if request.method == "POST":
            judul = request.form.get("judul", "").strip()
            id_penerbit = request.form.get("id_penerbit", "").strip()
            stok = request.form.get("stok", "").strip()

            if not judul or not id_penerbit or not stok:
                flash("Semua kolom wajib diisi.", "danger")
                return redirect(url_for("admin.tambah_buku"))

            try:
                id_penerbit = int(id_penerbit)
                stok = int(stok)

                if stok < 0 or id_penerbit <= 0:
                    raise ValueError
            except ValueError:
                flash("Penerbit dan stok harus berupa angka yang valid.", "danger")
                return redirect(url_for("admin.tambah_buku"))

            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO buku (judul, id_penerbit, stok)
                    VALUES (%s, %s, %s)
                    """,
                    (judul, id_penerbit, stok)
                )

            conn.commit()
            flash("Buku berhasil ditambahkan.", "success")
            return redirect(url_for("admin.tambah_buku"))

        with conn.cursor() as cur:
            cur.execute("""
                SELECT id_penerbit, nama_penerbit
                FROM penerbit
                ORDER BY nama_penerbit
            """)
            daftar_penerbit = cur.fetchall()

        return render_template(
            "admin_tambah_buku.html",
            daftar_penerbit=daftar_penerbit
        )

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@admin_bp.route("/buku/edit/<int:id_buku>", methods=["GET", "POST"])
@admin_required
def edit_buku(id_buku):
    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            if request.method == "POST":
                judul = request.form.get("judul", "").strip()
                id_penerbit = request.form.get("id_penerbit", "").strip()
                stok = request.form.get("stok", "").strip()

                try:
                    id_penerbit = int(id_penerbit)
                    stok = int(stok)

                    if not judul or id_penerbit <= 0 or stok < 0:
                        raise ValueError
                except ValueError:
                    flash("Data buku tidak valid.", "danger")
                    return redirect(
                        url_for("admin.edit_buku", id_buku=id_buku)
                    )

                cur.execute(
                    """
                    UPDATE buku
                    SET judul = %s, id_penerbit = %s, stok = %s
                    WHERE id_buku = %s
                    """,
                    (judul, id_penerbit, stok, id_buku)
                )

                if cur.rowcount == 0:
                    flash("Buku tidak ditemukan.", "danger")
                    return redirect(url_for("buku.dashboard"))

                conn.commit()
                flash("Buku berhasil diperbarui.", "success")
                return redirect(url_for("admin.edit_buku", id_buku=id_buku))

            cur.execute(
                """
                SELECT id_buku, judul, id_penerbit, stok
                FROM buku
                WHERE id_buku = %s
                """,
                (id_buku,)
            )
            buku = cur.fetchone()

            if not buku:
                flash("Buku tidak ditemukan.", "danger")
                return redirect(url_for("buku.dashboard"))

            cur.execute(
                """
                SELECT id_penerbit, nama_penerbit
                FROM penerbit
                ORDER BY nama_penerbit
                """
            )
            daftar_penerbit = cur.fetchall()

        return render_template(
            "admin_edit_buku.html",
            buku=buku,
            daftar_penerbit=daftar_penerbit
        )
    finally:
        conn.close()


@admin_bp.route("/buku/hapus/<int:id_buku>", methods=["POST"])
@admin_required
def hapus_buku(id_buku):
    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM buku WHERE id_buku = %s",
                (id_buku,)
            )

            if cur.rowcount == 0:
                flash("Buku tidak ditemukan.", "danger")
            else:
                conn.commit()
                flash("Buku berhasil dihapus.", "success")

    except Exception:
        conn.rollback()
        flash(
            "Buku tidak dapat dihapus. Mungkin masih digunakan dalam data peminjaman.",
            "danger"
        )
    finally:
        conn.close()

    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/peminjaman")
@admin_required
def daftar_peminjaman():
    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    pm.id_peminjaman,
                    u.nama,
                    u.email,
                    b.judul,
                    pm.tanggal_pinjam,
                    pm.status
                FROM peminjaman pm
                JOIN "user" u
                    ON pm.id_user = u.id_user
                JOIN buku b
                    ON pm.id_buku = b.id_buku
                ORDER BY pm.tanggal_pinjam DESC,
                         pm.id_peminjaman DESC
            """)
            daftar = cur.fetchall()

        return render_template(
            "admin_peminjaman.html",
            daftar_peminjaman=daftar
        )
    finally:
        conn.close()


@admin_bp.route(
    "/peminjaman/<int:id_peminjaman>/status",
    methods=["POST"]
)
@admin_required
def ubah_status_peminjaman(id_peminjaman):
    status_baru = request.form.get("status")

    if status_baru not in ("disetujui", "ditolak"):
        flash("Status tidak valid.", "danger")
        return redirect(url_for("admin.daftar_peminjaman"))

    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id_buku, status
                FROM peminjaman
                WHERE id_peminjaman = %s
                FOR UPDATE
            """, (id_peminjaman,))

            peminjaman = cur.fetchone()

            if peminjaman is None:
                flash("Data peminjaman tidak ditemukan.", "danger")

            elif peminjaman["status"] != "diajukan":
                flash(
                    "Pengajuan ini sudah diproses sebelumnya.",
                    "warning"
                )

            else:
                if status_baru == "ditolak":
                    cur.execute("""
                        UPDATE buku
                        SET stok = stok + 1
                        WHERE id_buku = %s
                    """, (peminjaman["id_buku"],))

                cur.execute("""
                    UPDATE peminjaman
                    SET status = %s
                    WHERE id_peminjaman = %s
                      AND status = 'diajukan'
                """, (status_baru, id_peminjaman))

                conn.commit()
                flash(
                    "Pengajuan berhasil " +
                    ("disetujui." if status_baru == "disetujui"
                     else "ditolak dan stok dikembalikan."),
                    "success"
                )
                return redirect(url_for("admin.daftar_peminjaman"))

        conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return redirect(url_for("admin.daftar_peminjaman"))



    

