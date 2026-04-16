nominal = int(input("jumlah belanja anda : "))

if (nominal>=100000) :
    diskon = 10
else :
    diskon = 0

PotonganHarga = nominal*diskon/100
total   = nominal-PotonganHarga

print("==" *20)
print("Diskon : " + str(diskon) + "%")
print("Potongan sebesar : Rp." + str(PotonganHarga))
print("Total Belanja : Rp." + str(total))