def format_alamat(jalan, kota, provinsi, kode_pos):
    """
    Menggabungkan komponen alamat menjadi satu string terformat.
 
    Parameter:
        jalan    (str): Nama jalan
        kota     (str): Nama kota
        provinsi (str): Nama provinsi
        kode_pos (str): Kode pos
 
    Return:
        str: Alamat lengkap dalam format standar
    """
    return f"Jalan: {jalan}, Kota: {kota}, {provinsi} ({kode_pos})"
 
hasil_3 = format_alamat("Jl. Mawar No. 10", "Sukabumi", "Jawa Barat", "43111")
print("=== Soal 3: Format Alamat ===")
print(hasil_3)
print()
 