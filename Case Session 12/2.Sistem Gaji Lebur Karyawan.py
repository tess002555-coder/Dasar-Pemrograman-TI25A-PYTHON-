UPAH_LEMBUR_PER_JAM = 50_000
BATAS_JAM_NORMAL    = 40
 
def hitung_gaji_lembur(gaji_pokok, total_jam_kerja):
  
    if total_jam_kerja > BATAS_JAM_NORMAL:
        jam_lembur  = total_jam_kerja - BATAS_JAM_NORMAL
        uang_lembur = jam_lembur * UPAH_LEMBUR_PER_JAM
        total_gaji  = gaji_pokok + uang_lembur
    else:
        total_gaji = gaji_pokok
    return total_gaji
 
hasil_2a = hitung_gaji_lembur(3_000_000, 45)   # lembur 5 jam
hasil_2b = hitung_gaji_lembur(3_000_000, 38)   # tidak lembur
print("=== Soal 2: Gaji Lembur ===")
print(f"Gaji pokok Rp3.000.000 | kerja 45 jam → Total: Rp{hasil_2a:,.0f}")
print(f"Gaji pokok Rp3.000.000 | kerja 38 jam → Total: Rp{hasil_2b:,.0f}")
print()
 