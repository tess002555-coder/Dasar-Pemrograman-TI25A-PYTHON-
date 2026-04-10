teks = "UNIVERSITAS NUSA PUTRA SUKABUMI"

# a
print("a =", teks[17:22].lower(), teks[12:16].lower())

# b
print("b =", teks.replace("U", ""))

# c
c_teks = teks.split()
c_teks = c_teks[::-1]
print("c =", " ".join(c_teks))

# d
b_teks = teks.split()
print("d =", b_teks[0][0] + b_teks[1][0] + b_teks[2][0] + b_teks[3][0])

# e
print("e =", f"{b_teks[0][-3:]} {b_teks[1][-2:]}{b_teks[2][0:2]} {b_teks[3]}")
