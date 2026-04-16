angka1 =int(input("Angka1 :"))
angka2 =int(input("Angka2 :"))
angka3 =int(input("Angka3 :"))

if (angka1>angka2 and angka1>angka3) :
    print ("angka terbesar : " + str(angka1))
    
elif (angka2>angka1 and angka2>angka3) :
    print ("angka terbesar : " + str(angka2))
else :
    print ("angka terbesar : " + str(angka3))