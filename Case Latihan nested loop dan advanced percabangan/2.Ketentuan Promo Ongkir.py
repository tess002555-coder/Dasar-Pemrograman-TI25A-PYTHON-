# input
total_belanja = int(input("Masukkan total belanja: "))
ongkir = int(input("Masukkan ongkir: "))
member = input("Apakah premium? (True/False): ") == "True"
hari = input("Hari transaksi: ").lower()

# ======================
# HITUNG ONGKIR
# ======================
if total_belanja >= 400000:
    diskon_ongkir = 1.0
elif total_belanja >= 250000:
    diskon_ongkir = 0.75
elif total_belanja >= 150000:
    diskon_ongkir = 0.5
else:
    diskon_ongkir = 0

ongkir_bayar = ongkir * (1 - diskon_ongkir)

# ======================
# HITUNG CASHBACK DASAR
# ======================
if total_belanja >= 300000:
    cashback = 0.10
elif total_belanja >= 200000:
    cashback = 0.07
elif total_belanja >= 100000:
    cashback = 0.05
else:
    cashback = 0

# ======================
# BONUS CASHBACK
# ======================
if member:
    cashback += 0.05

if hari == "sabtu":
    cashback += 0.03

# maksimal 15%
if cashback > 0.15:
    cashback = 0.15

jumlah_cashback = total_belanja * cashback

# ======================
# OUTPUT
# ======================
print("\n=== HASIL ===")
print("Ongkir bayar:", int(ongkir_bayar))
print("Cashback:", int(jumlah_cashback))