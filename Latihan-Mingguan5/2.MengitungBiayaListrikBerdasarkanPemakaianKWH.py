kwh = int(input("Masukkan total kwh: "))

if (kwh <= 100) :
    biaya = kwh * 500
elif (kwh <= 300) :
    biaya = kwh * 1000
elif (kwh <= 1000) :
    biaya = kwh * 2000

print (f"Total biaya yang harus dibayar adalah: ", biaya)