
from flask import Flask
from flask_bootstrap import Bootstrap5
from app.buku import buku_bp
from app.peminjaman import peminjaman_bp
from app.admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = "ganti-dengan-kunci-rahasia-acak"

    Bootstrap5(app)
    app.register_blueprint(buku_bp)
    app.register_blueprint(peminjaman_bp)
    app.register_blueprint(admin_bp)

    return app
