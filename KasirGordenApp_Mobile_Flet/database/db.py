import sqlite3
import json
import os

def get_connection():
    # Menunjuk langsung ke folder 'database' tempat file db.py ini berada
    base_dir = os.path.dirname(os.path.abspath(__file__ ))
    db_path = os.path.join(base_dir, "database.db")
    return sqlite3.connect(db_path)

def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Tabel Utama Pesanan (Ditambahkan kolom total_bayar jika belum ada)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pesanan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_pelanggan TEXT NOT NULL,
            nomor_hp TEXT NOT NULL,
            alamat TEXT,
            total_bayar INTEGER DEFAULT 0, -- Kolom untuk menyimpan total harga asli
            tanggal_dibuat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Jaga-jaga jika tabel pesanan sudah pernah dibuat sebelumnya tanpa kolom total_bayar
    cursor.execute("PRAGMA table_info(pesanan)")
    kolom = [k[1] for k in cursor.fetchall()]
    if 'total_bayar' not in kolom:
        cursor.execute("ALTER TABLE pesanan ADD COLUMN total_bayar INTEGER DEFAULT 0")
    
    # 2. Tabel Detail Ruangan (Terhubung ke tabel pesanan via pesanan_id)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detail_ruangan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pesanan_id INTEGER,
            nama_ruangan TEXT NOT NULL,
            data_gorden TEXT,
            data_vitrase TEXT,
            data_aksesoris TEXT,
            FOREIGN KEY (pesanan_id) REFERENCES pesanan(id) ON DELETE CASCADE
        )
    """)
    
    # 3. Tabel Login Admin
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def simpan_transaksi_baru(data_pesanan_lengkap):
    """
    Fungsi untuk menyimpan seluruh rangkaian data pesanan baru (Multi-Ruangan)
    ke SQLite secara aman menggunakan sistem transaksi (commit/rollback).
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Ambil nilai total harga kalkulasi dari dashboard, jika tidak ada default ke 0
        total_bayar = data_pesanan_lengkap.get("total_harga_kalkulasi", 0)
        
        # 1. Masukkan ke tabel 'pesanan' (Data Pelanggan & Total Bayar)
        cursor.execute("""
            INSERT INTO pesanan (nama_pelanggan, nomor_hp, alamat, total_bayar)
            VALUES (?, ?, ?, ?)
        """, (
            data_pesanan_lengkap["nama_pelanggan"],
            data_pesanan_lengkap["no_hp"],
            data_pesanan_lengkap["alamat"],
            total_bayar
        ))
        
        # Ambil ID pesanan yang baru saja di-insert untuk relasi foreign key
        id_pesanan_baru = cursor.lastrowid
        
        # 2. Iterasi dan masukkan tiap ruangan ke tabel 'detail_ruangan'
        for ruangan in data_pesanan_lengkap["daftar_ruangan"]:
            # Ubah data dictionary python menjadi format string JSON teks agar bisa masuk satu kolom SQLite
            json_gorden = json.dumps(ruangan["gorden"])
            json_vitrase = json.dumps(ruangan["vitrase"])
            json_aksesoris = json.dumps(ruangan["aksesoris"])
            
            cursor.execute("""
                INSERT INTO detail_ruangan (pesanan_id, nama_ruangan, data_gorden, data_vitrase, data_aksesoris)
                VALUES (?, ?, ?, ?, ?)
            """, (
                id_pesanan_baru,
                ruangan["nama_ruangan"],
                json_gorden,
                json_vitrase,
                json_aksesoris
            ))
            
        # Jika semua proses input berhasil tanpa kendala, lakukan commit permanen
        conn.commit()
        return True, "Sukses"
        
    except Exception as e:
        # Jika di tengah jalan ada satu proses yang error, batalkan seluruh rangkaian input agar database tidak korup/pincang
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def ambil_semua_pesanan():
    import sqlite3
    import os
    
    # Ambil path database yang valid
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "database", "database.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # --- JAMINAN AMAN: Cek & Tambah Kolom total_bayar jika belum ada ---
    try:
        cursor.execute("ALTER TABLE pesanan ADD COLUMN total_bayar INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass # Kolom sudah ada, abaikan error
        
    # Ambil data lengkap termasuk total_bayar sesuai kebutuhan riwayat_transaksi.py
    cursor.execute("SELECT id, nama_pembeli, no_hp, alamat, total_bayar, tanggal FROM pesanan ORDER BY id DESC")
    hasil = cursor.fetchall()
    
    conn.close()
    return hasil

def hapus_pesanan_by_id(id_pesanan):
    """
    Fungsi untuk menghapus data pesanan berdasarkan ID.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM pesanan WHERE id = ?", (id_pesanan,))
        conn.commit()
    except Exception as e:
        print(f"Error saat menghapus data: {str(e)}")
    finally:
        conn.close()

def buat_tabel_barang():
    """Fungsi untuk membuat tabel master data harga barang/kain"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS barang (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_barang TEXT NOT NULL,
            kategori TEXT NOT NULL,
            harga_per_meter INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

import sqlite3
import os

def tambah_kolom_total_bayar():
    # Menentukan path database agar selalu tepat
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "database.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Perintah SQL untuk menambahkan kolom total_bayar jika belum ada
        cursor.execute("ALTER TABLE pesanan ADD COLUMN total_bayar INTEGER DEFAULT 0;")
        conn.commit()
        conn.close()
        print("Kolom total_bayar berhasil ditambahkan otomatis!")
    except sqlite3.OperationalError:
        # Jika kolom sudah ada, abaikan error agar aplikasi tidak crash
        print("Kolom total_bayar sudah ada.")