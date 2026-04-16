password_benar = "babang tamvan"
percobaan = 0

while percobaan < 3 :
    password_input = input("Masukkan Password: ")
    if password_input == password_benar :
        print("Login Berhasil")
        break
    else:
        percobaan += 1
        print ("Password salah. Percobaan ke-", percobaan)
    if percobaan == 3:
        print ("Akun Terkunci")