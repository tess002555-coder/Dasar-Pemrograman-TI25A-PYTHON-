def konversi_menit(jumlah_episode, durasi_per_episode):
    
    total_menit = jumlah_episode * durasi_per_episode
    jam         = total_menit // 60
    menit_sisa  = total_menit % 60
    return jam, menit_sisa
 
jam, menit = konversi_menit(12, 45)   # 12 episode x 45 menit
print("=== Soal 4: Binge-Watching ===")
print(f"12 episode × 45 menit = {jam} jam {menit} menit")
print()