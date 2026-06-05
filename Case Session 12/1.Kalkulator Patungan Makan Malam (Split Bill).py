def hitung_patungan(total_nota, jumlah_orang, persen_tips):
    
    total_dengan_tips = total_nota + (total_nota * persen_tips / 100)
    bayar_per_orang = total_dengan_tips / jumlah_orang
    return bayar_per_orang
 
hasil_1 = hitung_patungan(300000, 4, 10)
print("=== Soal 1: Split Bill ===")
print(f"Total nota: Rp300.000 | 4 orang | tips 10%")
print(f"Bayar per orang: Rp{hasil_1:,.0f}")
print()
 