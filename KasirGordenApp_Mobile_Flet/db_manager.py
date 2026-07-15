import sqlite3

def init_db():
    conn = sqlite3.connect('kasir_gorden.db')
    cursor = conn.cursor()
    # Tabel Pesanan Utama
    cursor.execute('''CREATE TABLE IF NOT EXISTS pesanan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_pelanggan TEXT,
        no_hp TEXT,
        total_harga REAL)''')
    # Tabel Detail Ruangan
    cursor.execute('''CREATE TABLE IF NOT EXISTS pesanan_ruangan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pesanan_id INTEGER,
        nama_ruangan TEXT,
        jenis_kain TEXT,
        FOREIGN KEY(pesanan_id) REFERENCES pesanan(id))''')
    # Tabel Barang
    cursor.execute('''CREATE TABLE IF NOT EXISTS barang (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        nama TEXT, 
        harga TEXT)''')
    conn.commit()
    conn.close()

def simpan_data_pesanan(nama, hp, total, list_ruangan):
    conn = sqlite3.connect('kasir_gorden.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO pesanan (nama_pelanggan, no_hp, total_harga) VALUES (?, ?, ?)', (nama, hp, total))
    pesanan_id = cursor.lastrowid
    for r in list_ruangan:
        cursor.execute('INSERT INTO pesanan_ruangan (pesanan_id, nama_ruangan, jenis_kain) VALUES (?, ?, ?)', 
                       (pesanan_id, r['nama'], r['kain']))
    conn.commit()
    conn.close()

def get_semua_pesanan():
    conn = sqlite3.connect('kasir_gorden.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nama_pelanggan, no_hp, total_harga FROM pesanan')
    data = cursor.fetchall()
    conn.close()
    return data