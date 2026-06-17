def konversi_nilai(nilai):
    if nilai == 'A':
        return 4
    elif nilai == 'B':
        return 3
    elif nilai == 'C':
        return 2
    elif nilai == 'D':
        return 1
    else:
        return 0


jumlah_mahasiswa = int(input("Masukkan jumlah mahasiswa: "))

data_mahasiswa = []
total_ipk_kelas = 0

for i in range(jumlah_mahasiswa):
    print(f"\nMahasiswa ke-{i+1}")
    nama = input("Nama mahasiswa: ")
    jumlah_mk = int(input("Jumlah mata kuliah: "))

    total_bobot = 0
    total_sks = 0

    for j in range(jumlah_mk):
        print(f"\nMata kuliah {j+1}")
        nama_mk = input("Nama mata kuliah: ")
        sks = int(input("SKS: "))
        nilai = input("Nilai (A/B/C/D/E): ").upper()

        bobot = konversi_nilai(nilai)

        total_bobot += bobot * sks
        total_sks += sks

    ipk = total_bobot / total_sks

    data_mahasiswa.append([nama, ipk])
    total_ipk_kelas += ipk

print("\n=== HASIL IPK MAHASISWA ===")
for mahasiswa in data_mahasiswa:
    print(f"{mahasiswa[0]} : {mahasiswa[1]:.2f}")

rata_rata_ipk = total_ipk_kelas / jumlah_mahasiswa

print(f"\nRata-rata IPK kelas: {rata_rata_ipk:.2f}")