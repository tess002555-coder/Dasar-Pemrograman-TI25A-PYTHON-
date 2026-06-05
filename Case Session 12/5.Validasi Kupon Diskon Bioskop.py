KODE_KUPON_VALID  = "NONTONSERU"
DISKON_NOMINAL    = 15_000
MINIMAL_TIKET     = 2
 
def cek_diskon(total_harga, jumlah_tiket, kode_kupon):
    """
    Menerapkan diskon jika kupon valid dan syarat tiket terpenuhi.
 
    Parameter:
        total_harga   (float): Total harga tiket sebelum diskon
        jumlah_tiket  (int)  : Jumlah tiket yang dibeli
        kode_kupon    (str)  : Kode kupon yang dimasukkan pembeli
 
    Return:
        float: Harga akhir setelah pengecekan kupon
    """
    if kode_kupon == KODE_KUPON_VALID and jumlah_tiket >= MINIMAL_TIKET:
        return total_harga - DISKON_NOMINAL
    return total_harga
 
hasil_5a = cek_diskon(100_000, 2, "NONTONSERU")   # syarat terpenuhi
hasil_5b = cek_diskon(100_000, 1, "NONTONSERU")   # tiket kurang
hasil_5c = cek_diskon(100_000, 3, "DISKON123")    # kode salah
print("=== Soal 5: Kupon Diskon ===")
print(f"Rp100.000 | 2 tiket | kode benar  → Rp{hasil_5a:,.0f}")
print(f"Rp100.000 | 1 tiket | kode benar  → Rp{hasil_5b:,.0f}")
print(f"Rp100.000 | 3 tiket | kode salah  → Rp{hasil_5c:,.0f}")
print()