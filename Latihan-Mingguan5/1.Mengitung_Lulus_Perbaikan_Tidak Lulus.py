nilai = int (input("masukan Nilai Siswa : "))
absensi = int (input("Masukkan jumlah Absensi Siswa : "))

if (nilai>=70 and absensi>=50) :
    print ("Siswa Lulus !!!")
elif (nilai<70 and absensi>=70) or (nilai>=70 and absensi<50) :
    print ("Diperbolehkan mengulang !!!")
else :
    print ("Murid tidak terselamtkan !!!")