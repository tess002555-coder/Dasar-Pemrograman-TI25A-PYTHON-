import sqlite3

def inisialisasi_db():
    conn = sqlite3.connect("gorden_bisnis.db")
    cursor = conn.cursor()
    
    # Tabel Produk (Kain/Aksesoris)
    cursor.execute('''CREATE TABLE IF NOT EXISTS produk (
                        id INTEGER PRIMARY KEY,
                        nama_produk TEXT,
                        stok REAL,
                        harga_per_meter REAL)''')
    
    # Tabel Transaksi
    cursor.execute('''CREATE TABLE IF NOT EXISTS transaksi (
                        id INTEGER PRIMARY KEY,
                        nama_pelanggan TEXT,
                        detail_pesanan TEXT,
                        total_harga REAL,
                        tanggal DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    inisialisasi_db()
    print("Database berhasil dibuat!")