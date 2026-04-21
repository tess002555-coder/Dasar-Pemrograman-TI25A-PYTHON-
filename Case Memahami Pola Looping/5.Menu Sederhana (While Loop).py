pilih = 0

while pilih != 2:
    print("1. Halo")
    print("2. Keluar")
    
    pilih = int(input("Pilih menu: "))

    if pilih == 1:
        print("Halo User")
        
    elif pilih == 2:
        print("Program berhenti")
        
    else:
        print("Pilihan salah")