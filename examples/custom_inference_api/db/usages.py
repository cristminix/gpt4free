from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func, select, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.sqlite import DATETIME
from datetime import datetime
from typing import Optional, List, Dict, Any
import asyncio

# Membuat base class untuk model SQLAlchemy
Base = declarative_base()

# Definisi model Usage menggunakan SQLAlchemy
class UsageModel(Base):
    __tablename__ = 'usages'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    provider = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    date = Column(Text, nullable=False)
    connections = Column(Integer, nullable=False)
    tokens = Column(Integer, nullable=False)
    ipaddr = Column(Text, nullable=True)
    updated_at = Column(Text, nullable=False, default=datetime.utcnow().isoformat() + "Z")

# Koneksi database dengan SQLAlchemy
DB_PATH = "sqlite:///examples/gpt4free.db"
engine = create_engine(DB_PATH, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

# Definisi kelas Usage (untuk kompatibilitas dengan kode yang ada)
class Usage:
    def __init__(self, id: int, provider: str, model: str, date: str, connections: int, tokens: int, ipaddr: Optional[str], updated_at: str):
        self.id = id
        self.provider = provider
        self.model = model
        self.date = date
        self.connections = connections
        self.tokens = tokens
        self.ipaddr = ipaddr
        self.updated_at = updated_at

# Fungsi-fungsi dari kode JavaScript yang dikonversi ke Python dengan SQLAlchemy

async def upsert_usage(
    provider: str,
    model: str,
    date: str,
    connections: int,
    tokens: int,
    ipaddr: str = ""
) -> Usage:
    """
    Mengupdate atau memasukkan record penggunaan API ke database berdasarkan tanggal
    @param provider Nama provider
    @param model Nama model
    @param date Tanggal dalam format 2020-09-09
    @param connections Jumlah koneksi
    @param tokens Jumlah token
    @returns Data usage yang disimpan
    """
    # Mengecek apakah sudah ada record dengan kombinasi provider, model, dan date tertentu
    existing_record: Optional[Usage] = await get_usage_by_provider_model_date(
        provider,
        model,
        date,
        ipaddr
    )

    if existing_record:
        # Jika ada, mengupdate field connections, tokens, dan updated_at
        updated_usage: Usage = await update_usage(
            existing_record.id,
            connections,
            tokens,
            ipaddr
        )
        return updated_usage
    else:
        # Jika tidak ada, memasukkan record baru
        new_usage: Usage = await insert_usage(
            provider,
            model,
            date,
            connections,
            tokens,
            ipaddr
        )
        return new_usage

async def insert_usage(
    provider: str,
    model: str,
    date: str,
    connections: int,
    tokens: int,
    ipaddr: str = ""
) -> Usage:
    """
    Memasukkan record penggunaan API baru ke database
    @param provider Nama provider
    @param model Nama model
    @param date Tanggal dalam format 2020-09-09
    @param connections Jumlah koneksi
    @param tokens Jumlah token
    @returns Data usage yang disimpan
    """
    updated_at = datetime.utcnow().isoformat() + "Z"
    
    db = SessionLocal()
    try:
        # Membuat objek UsageModel
        db_usage = UsageModel(
            provider=provider,
            model=model,
            date=date,
            connections=connections,
            tokens=tokens,
            ipaddr=ipaddr,
            updated_at=updated_at
        )
        
        # Menambahkan ke database
        db.add(db_usage)
        db.commit()
        db.refresh(db_usage)
        
        # Mengembalikan objek Usage yang dibuat
        return Usage(
            id=db_usage.id,
            provider=db_usage.provider,
            model=db_usage.model,
            date=db_usage.date,
            connections=db_usage.connections,
            tokens=db_usage.tokens,
            ipaddr=db_usage.ipaddr,
            updated_at=db_usage.updated_at
        )
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

async def update_usage(
    id: int,
    connections: int,
    tokens: int,
    ipaddr: str = ""
) -> Usage:
    """
    Mengupdate record penggunaan API di database
    @param id ID record yang akan diupdate
    @param connections Jumlah koneksi
    @param tokens Jumlah token
    @returns Data usage yang diperbarui
    """
    updated_at = datetime.utcnow().isoformat() + "Z"
    
    db = SessionLocal()
    try:
        # Mencari record berdasarkan ID
        db_usage = db.query(UsageModel).filter(UsageModel.id == id).first()
        
        if not db_usage:
            raise Exception(f"Record dengan id {id} tidak ditemukan")
        
        # Mengupdate field-field
        db_usage.connections = connections
        db_usage.tokens = tokens
        db_usage.updated_at = updated_at
        
        # Mengupdate ipaddr jika disediakan
        if ipaddr:
            db_usage.ipaddr = ipaddr
            
        db.commit()
        db.refresh(db_usage)
        
        # Mengembalikan objek Usage yang diperbarui
        return Usage(
            id=db_usage.id,
            provider=db_usage.provider,
            model=db_usage.model,
            date=db_usage.date,
            connections=db_usage.connections,
            tokens=db_usage.tokens,
            ipaddr=db_usage.ipaddr,
            updated_at=db_usage.updated_at
        )
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

async def get_usage_by_provider_model_date(
    provider: str,
    model: str,
    date: str,
    ipaddr: str = ""
) -> Optional[Usage]:
    """
    Mendapatkan record penggunaan API dari database berdasarkan provider, model, dan date
    @param provider Nama provider
    @param model Nama model
    @param date Tanggal dalam format 2020-09-09
    @returns Data usage jika ditemukan, None jika tidak
    """
    db = SessionLocal()
    try:
        # Membangun query berdasarkan apakah ipaddr disediakan
        if ipaddr:
            db_usage = db.query(UsageModel).filter(
                and_(
                    UsageModel.provider == provider,
                    UsageModel.model == model,
                    UsageModel.date == date,
                    UsageModel.ipaddr == ipaddr
                )
            ).first()
        else:
            db_usage = db.query(UsageModel).filter(
                and_(
                    UsageModel.provider == provider,
                    UsageModel.model == model,
                    UsageModel.date == date
                )
            ).first()
        
        if db_usage:
            return Usage(
                id=db_usage.id,
                provider=db_usage.provider,
                model=db_usage.model,
                date=db_usage.date,
                connections=db_usage.connections,
                tokens=db_usage.tokens,
                ipaddr=db_usage.ipaddr,
                updated_at=db_usage.updated_at
            )
        else:
            return None
    finally:
        db.close()

async def get_all_usages() -> List[Usage]:
    """
    Mendapatkan semua record penggunaan API dari database
    @returns Array dari data usage
    """
    db = SessionLocal()
    try:
        db_usages = db.query(UsageModel).all()
        
        usages = []
        for db_usage in db_usages:
            usages.append(Usage(
                id=db_usage.id,
                provider=db_usage.provider,
                model=db_usage.model,
                date=db_usage.date,
                connections=db_usage.connections,
                tokens=db_usage.tokens,
                ipaddr=db_usage.ipaddr,
                updated_at=db_usage.updated_at
            ))
        
        return usages
    finally:
        db.close()

async def get_usages_by_provider(
    provider: str,
    ipaddr: Optional[str] = None
) -> Optional[Dict[str, int]]:
    """
    Mendapatkan record penggunaan API dari database berdasarkan provider
    @param provider Nama provider
    @param ipaddr Alamat IP (opsional)
    @returns Object dengan total connections dan tokens untuk hari ini
    """
    from datetime import datetime
    current_date = datetime.utcnow().strftime("%Y-%m-%d")
    
    db = SessionLocal()
    try:
        # Membangun query berdasarkan apakah ipaddr disediakan
        if ipaddr:
            result = db.query(
                func.sum(UsageModel.connections).label('total_connections'),
                func.sum(UsageModel.tokens).label('total_tokens')
            ).filter(
                and_(
                    UsageModel.provider == provider,
                    UsageModel.date == current_date,
                    UsageModel.ipaddr == ipaddr
                )
            ).first()
        else:
            result = db.query(
                func.sum(UsageModel.connections).label('total_connections'),
                func.sum(UsageModel.tokens).label('total_tokens')
            ).filter(
                and_(
                    UsageModel.provider == provider,
                    UsageModel.date == current_date
                )
            ).first()
        
        # Jika tidak ada data, kembalikan None
        if not result or (result.total_connections is None and result.total_tokens is None):
            return None
        
        # Kembalikan object dengan nilai default 0 jika None
        return {
            "connections": result.total_connections if result.total_connections is not None else 0,
            "tokens": result.total_tokens if result.total_tokens is not None else 0
        }
    finally:
        db.close()

# Inisialisasi database saat modul diimport
init_db()