harga = int(input("Masukkan Total Belanja: "))

if (harga >= 500000) :
    diskon = harga * 0.20
    print ("diskon 20%")
    print ("jumlah diskon: ", diskon)

elif (harga >= 300000) :
    diskon = harga * 0.10
    print ("diskon 10%")
    print ("jumlah diskon: ", diskon)

elif (harga >= 100000) :
    diskon = harga * 0.05
    print ("diskon 5%")
    print ("jumlah diskon: ", diskon)

else : 
    diskon = 0
    print ("Tidak ada Diskon")

print("Total yang harus dibayar: ", harga - diskon)