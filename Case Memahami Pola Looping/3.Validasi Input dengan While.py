angka = int(input("Masukkan angka positif: "))

while angka < 0:
    print("Angka tidak boleh negatif")
    angka = int(input("Masukkan angka positif lagi: "))

print("Angka yang dimasukkan =", angka)