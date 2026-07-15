from reportlab.pdfgen import canvas

def buat_laporan_progres():
    nama_file = "Progress_Pengembangan_Aplikasi_Kasir_Gorden.pdf"
    c = canvas.Canvas(nama_file)
    
    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, "Laporan Progres Pengembangan: Aplikasi Kasir Gorden")
    c.setFont("Helvetica", 12)
    c.drawString(50, 780, "Tanggal: 25 Juni 2026")
    
    # Isi Laporan
    teks = [
        "1. Lingkungan Pengembangan: Python, CustomTkinter (UI Modern), SQLite (Database).",
        "2. Fitur yang Telah Diimplementasikan:",
        "   - Database terintegrasi untuk menyimpan data transaksi.",
        "   - Antarmuka (GUI) modern dengan CustomTkinter.",
        "   - Logika perhitungan otomatis (Rumus Gorden: L*2 * T * Harga).",
        "   - Sistem manajemen data (Create, Read, Delete).",
        "   - Fitur Cetak Struk (Export PDF menggunakan ReportLab).",
        "",
        "3. Roadmap Selanjutnya:",
        "   - Packaging menjadi file .exe agar bisa dijalankan di Windows tanpa instal Python.",
        "   - Optimasi layout untuk kebutuhan layar kasir (POS).",
        "   - Penambahan fitur manajemen stok kain."
    ]
    
    y = 740
    for baris in teks:
        c.drawString(50, y, baris)
        y -= 20
        
    c.save()
    print(f"Laporan berhasil dibuat: {nama_file}")

if __name__ == "__main__":
    buat_laporan_progres()