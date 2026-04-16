masa_kerja = int(input("Masukkan Jumlah Tahun Masa Kerja Karyawan: "))
peforma = input("Masukkan Peforma Karyawan (baik/buruk): ")

if masa_kerja >= 5 and peforma == "baik" :
    print ("Bonus Besar")
elif masa_kerja >= 5 and peforma == "buruk" :
    print ("Bonus Kecil")
elif masa_kerja < 5 and peforma == "baik" :
    print ("Bonus Kecil")
else :
    print ("Tanpa Bonus")