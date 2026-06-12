from Aritmatika import *
from Konversi import *
from Ubah_bilangan import *

while True:
    print("----- MENU UTAMA -----")
    print("1. Aritmatika")
    print("2. Konversi")
    print("3. Ubah Bilangan")
    print("4. Keluar")

    pilihan = input("Pilih menu: ")

    if pilihan == "1":
        print("----- Aritmatika -----")
        print("1. Penjumlahan")
        print("2. Perpangkatan")
        print("3. Perkalian")

        pilih = input("Pilih operasi: ")

        a = float(input("Bilangan pertama: "))
        b = float(input("Bilangan kedua: "))

        if pilih == "1":
            print("Hasil =", penjumlahan(a, b))

        elif pilih == "2":
            print("Hasil =", perpangkatan(a, b))

        elif pilih == "3":
            print("Hasil =", perkalian(a, b))

        else:
            print("Pilihan tidak valid!")

    elif pilihan == "2":
        print("----- Konversi -----")
        print("1. CM ke M")
        print("2. M ke CM")

        pilih = input("Pilih konversi: ")

        angka = float(input("Masukkan nilai: "))

        if pilih == "1":
            print("Hasil =", cm_ke_m(angka), "m")

        elif pilih == "2":
            print("Hasil =", m_ke_cm(angka), "cm")

        else:
            print("Pilihan tidak valid!")

    elif pilihan == "3":
        print("----- Ubah Bilangan -----")
        print("1. Desimal ke Biner")
        print("2. Desimal ke Oktal")
        print("3. Desimal ke Heksadesimal")

        pilih = input("Pilih konversi: ")

        angka = int(input("Masukkan bilangan desimal: "))

        if pilih == "1":
            print("Hasil =", desimal_ke_biner(angka))

        elif pilih == "2":
            print("Hasil =", desimal_ke_oktal(angka))

        elif pilih == "3":
            print("Hasil =", desimal_ke_heksadesimal(angka))

        else:
            print("Pilihan tidak valid!")

    elif pilihan == "4":
        print("Terima kasih.")
        break

    else:
        print("Pilihan tidak valid!")