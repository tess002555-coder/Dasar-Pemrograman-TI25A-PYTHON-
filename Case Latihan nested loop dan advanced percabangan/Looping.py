rows = 5
cols = 5

# ======================
# BLOK ATAS (5 baris)
# ======================
for i in range(rows):
    for j in range(cols):
        
        # baris 0,1,3,4 → - - * - -
        if i in [0, 1, 3, 4]:
            if j == 2:
                print("*", end=" ")
            else:
                print("-", end=" ")
        
        # baris 2 → semua *
        elif i == 2:
            print("*", end=" ")
    
    print()

# spasi pemisah (opsional)
print()

# ======================
# BLOK BAWAH (5 baris)
# ======================
for i in range(rows):
    for j in range(cols):
        
        # baris 0 → semua *
        if i == 0 or i == 4:
            print("*", end=" ")
        
        # baris 1-3 → * - - - *
        else:
            if j == 0 or j == cols - 1:
                print("*", end=" ")
            else:
                print("-", end=" ")
    
    print()