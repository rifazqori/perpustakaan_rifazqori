from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from buku import buku_bp
from peminjaman import peminjaman_bp

app = Flask(__name__)
app.secret_key = "kunci-rahasia-perpustakaan-2026"
Bootstrap5(app)

app.register_blueprint(buku_bp)
app.register_blueprint(peminjaman_bp)

if __name__ == "__main__":
    app.run(debug=True)
