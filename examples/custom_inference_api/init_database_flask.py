#!/usr/bin/env python3
"""
Script untuk menginisialisasi database menggunakan Flask-SQLAlchemy
"""

import os
from flask import Flask
from examples.custom_inference_api.db.models import base_db

# Membuat direktori jika belum ada
db_dir = os.path.dirname('examples/gpt4free.db')
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

# Membuat aplikasi Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///examples/gpt4free.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inisialisasi database dengan aplikasi
base_db.init_app(app)

def init_db():
    """Inisialisasi database dan membuat tabel jika belum ada"""
    with app.app_context():
        # Membuat semua tabel
        base_db.create_all()
        print("Database berhasil diinisialisasi!")

if __name__ == "__main__":
    init_db()