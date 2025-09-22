from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Membuat base class untuk model SQLAlchemy
Base = declarative_base()

# Koneksi database dengan SQLAlchemy
DB_PATH = "sqlite:///gpt4free.db"
engine = create_engine(DB_PATH, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Membuat kelas untuk menyimulasikan Flask-SQLAlchemy
class BaseDB:
    def __init__(self, engine, session_local):
        self.engine = engine
        self.session_local = session_local
    
    @property
    def session(self):
        # Membuat session baru setiap kali diakses
        return self.session_local()
    
    def query(self, *args):
        # Membuat session dan melakukan query
        return self.session.query(*args)

# Membuat instance base_db untuk kompatibilitas dengan kode yang ada
base_db = BaseDB(engine, SessionLocal)

# Fungsi untuk mendapatkan session database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inisialisasi database
def init_db():
    """Inisialisasi database dan membuat tabel jika belum ada"""
    Base.metadata.create_all(bind=engine)