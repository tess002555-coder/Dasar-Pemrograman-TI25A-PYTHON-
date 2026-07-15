from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QGroupBox, QScrollArea, QComboBox, QMessageBox, QCompleter)
from PyQt6.QtCore import Qt
from PyQt6.QtCore import Qt, pyqtSignal, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
import os
import sys
import sqlite3

class ClickableLabel(QLabel):
    clicked = pyqtSignal(int)
    def __init__(self, index, text, parent=None):
        super().__init__(text, parent)
        self.index = index
    def mousePressEvent(self, event):
        self.clicked.emit(self.index)
        
class DashboardInput(QWidget):
    transaksi_disimpan = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.list_ruangan_input = []
        self.index_ruangan_aktif = 0
        
        self.master_barang = {}
        self.harga_barang_map = {}
        self.ambil_master_barang_db()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)
        
        # --- Header ---
        title = QLabel("INPUT TRANSAKSI PESANAN BARU")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #a78bfa; letter-spacing: 1px;")
        main_layout.addWidget(title)
        
        # --- 1. Data Pelanggan ---
        grup_pelanggan = QGroupBox("DATA PELANGGAN")
        grup_pelanggan.setStyleSheet("""
            QGroupBox { font-weight: bold; color: #a78bfa; border: 1px solid #374151; border-radius: 8px; margin-top: 15px; padding-top: 15px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; }
            QLabel { color: #e5e7eb; font-size: 13px; font-weight: bold; }
            QLineEdit { background-color: #1f2937; color: white; border: 1px solid #374151; padding: 8px; border-radius: 6px; }
            QLineEdit:focus { border-color: none; }
        """)
        
        layout_pelanggan = QHBoxLayout(grup_pelanggan)
        col_nama = QVBoxLayout()
        col_nama.addWidget(QLabel("Nama Pembeli:"))
        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Masukkan nama lengkap...")
        col_nama.addWidget(self.input_nama)
        
        col_hp = QVBoxLayout()
        col_hp.addWidget(QLabel("No. HP / WA:"))
        self.input_hp = QLineEdit()
        self.input_hp.setPlaceholderText("Contoh: 08123456xxx")
        col_hp.addWidget(self.input_hp)
        
        col_alamat = QVBoxLayout()
        col_alamat.addWidget(QLabel("Alamat Pengiriman:"))
        self.input_alamat = QLineEdit()
        self.input_alamat.setPlaceholderText("Alamat lengkap lokasi pemasangan...")
        col_alamat.addWidget(self.input_alamat)
        
        layout_pelanggan.addLayout(col_nama, 2)
        layout_pelanggan.addLayout(col_hp, 2)
        layout_pelanggan.addLayout(col_alamat, 3)
        main_layout.addWidget(grup_pelanggan)
        
        # --- 2. Multi-Ruangan ---
        layout_konten_order = QHBoxLayout()
        layout_konten_order.setSpacing(20)
        
        self.layout_nav_kiri = QVBoxLayout()
        self.btn_tambah_ruang = QPushButton("➕ Tambah Ruangan")
        self.btn_tambah_ruang.setStyleSheet("""
            QPushButton { background-color: #1e293b; color: #a78bfa; border: 1px solid #4f46e5; padding: 10px; font-weight: bold; border-radius: 6px; }
            QPushButton:hover { background-color: #4f46e5; color: white; }
        """)
        self.btn_tambah_ruang.clicked.connect(self.tambah_ruangan_baru)
        self.layout_nav_kiri.addWidget(self.btn_tambah_ruang)
        
        self.scroll_nav = QScrollArea()
        self.scroll_nav.setWidgetResizable(True)
        self.scroll_nav.setFixedWidth(180)
        self.scroll_nav.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.widget_list_ruang = QWidget()
        self.widget_list_ruang.setStyleSheet("background-color: #111827;")
        self.layout_list_tombol_ruang = QVBoxLayout(self.widget_list_ruang)
        self.layout_list_tombol_ruang.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_nav.setWidget(self.widget_list_ruang)
        self.layout_nav_kiri.addWidget(self.scroll_nav)
        layout_konten_order.addLayout(self.layout_nav_kiri)
        
        self.grup_detail_ruang = QGroupBox("SPESIFIKASI RUANGAN")
        self.grup_detail_ruang.setStyleSheet("""
            QGroupBox { font-weight: bold; color: #f59e0b; border: 1px solid #374151; border-radius: 8px; padding-top: 15px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; }
            QLabel { color: #e5e7eb; font-size: 13px; }
            QLineEdit, QComboBox { background-color: #1f2937; color: white; border: 1px solid #374151; padding: 6px; border-radius: 6px; }
            QComboBox QAbstractItemView { background-color: #1f2937; color: white; selection-background-color: #4f46e5; }
        """)
        self.layout_detail_ruang = QVBoxLayout(self.grup_detail_ruang)
        
        layout_nama_r = QHBoxLayout()
        layout_nama_r.addWidget(QLabel("Nama Ruangan / Jendela:"))
        self.input_nama_ruang_detail = QLineEdit()
        self.input_nama_ruang_detail.textChanged.connect(self.sinkronisasi_nama_ruangan)
        layout_nama_r.addWidget(self.input_nama_ruang_detail, 2)
        
        self.btn_hapus_ruang = QPushButton("🗑️ Hapus Ruangan")
        self.btn_hapus_ruang.setStyleSheet("background-color: #ef4444; color: white; padding: 6px 12px; font-weight: bold; border-radius: 6px; border: none;")
        self.btn_hapus_ruang.clicked.connect(self.hapus_ruangan_aktif)
        layout_nama_r.addWidget(self.btn_hapus_ruang)
        self.layout_detail_ruang.addLayout(layout_nama_r)
        
        layout_spek_kain = QHBoxLayout()
        
        # BOX GORDEN
        box_gorden = QGroupBox("GORDEN")
        box_gorden.setStyleSheet("QGroupBox { color: #38bdf8; border: 1px solid #1e293b; }")
        lay_g = QVBoxLayout(box_gorden)
        lay_g_dimensi = QHBoxLayout()
        lay_g_dimensi.addWidget(QLabel("L (m):"))
        self.inp_g_l = QLineEdit()
        self.inp_g_l.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[0-9]*[.,]?[0-9]{0,2}$")))
        lay_g_dimensi.addWidget(self.inp_g_l)
        lay_g_dimensi.addWidget(QLabel("T (m):"))
        self.inp_g_t = QLineEdit()
        self.inp_g_t.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[0-9]*[.,]?[0-9]{0,2}$")))
        lay_g_dimensi.addWidget(self.inp_g_t)
        lay_g.addLayout(lay_g_dimensi)
        
        lay_g.addWidget(QLabel("Pilih Kain Gorden:"))
        self.cmb_g_tipe = QComboBox()
        self.buat_combo_bisa_dicari(self.cmb_g_tipe)
        lay_g.addWidget(self.cmb_g_tipe)
        
        # PINDAH KE SINI: Batangan Rel Gorden
        lay_g.addWidget(QLabel("📏 Batangan / Rel Gorden:"))
        self.cmb_a_batang = QComboBox()
        self.buat_combo_bisa_dicari(self.cmb_a_batang)
        lay_g.addWidget(self.cmb_a_batang)
        
        layout_spek_kain.addWidget(box_gorden)
        
        # BOX VITRASE
        box_vitrase = QGroupBox("VITRASE")
        box_vitrase.setStyleSheet("QGroupBox { color: #ec4899; border: 1px solid #1e293b; }")
        lay_v = QVBoxLayout(box_vitrase)
        lay_v_dimensi = QHBoxLayout()
        lay_v_dimensi.addWidget(QLabel("L (m):"))
        self.inp_v_l = QLineEdit()
        self.inp_v_l.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[0-9]*[.,]?[0-9]{0,2}$")))
        lay_v_dimensi.addWidget(self.inp_v_l)
        lay_v_dimensi.addWidget(QLabel("T (m):"))
        self.inp_v_t = QLineEdit()
        self.inp_v_t.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[0-9]*[.,]?[0-9]{0,2}$")))
        lay_v_dimensi.addWidget(self.inp_v_t)
        lay_v.addLayout(lay_v_dimensi)
        
        lay_v.addWidget(QLabel("Pilih Kain Vitrase:"))
        self.cmb_v_tipe = QComboBox()
        self.buat_combo_bisa_dicari(self.cmb_v_tipe)
        lay_v.addWidget(self.cmb_v_tipe)
        
        # PINDAH KE SINI: Batangan Rel Vitrase
        lay_v.addWidget(QLabel("📏 Batangan / Rel Vitrase:"))
        self.cmb_a_batang_vitrase = QComboBox()
        self.buat_combo_bisa_dicari(self.cmb_a_batang_vitrase)
        lay_v.addWidget(self.cmb_a_batang_vitrase)
        
        layout_spek_kain.addWidget(box_vitrase)
        
        self.layout_detail_ruang.addLayout(layout_spek_kain)
        
        # BOX AKSESORIS OTOMATIS
        box_aksesoris = QGroupBox("AKSESORIS & KELENGKAPAN (VOLUME OTOMATIS)")
        box_aksesoris.setStyleSheet("QGroupBox { color: #10b981; border: 1px solid #1e293b; }")
        lay_a = QVBoxLayout(box_aksesoris)
        
        # Baris 1: Renda Gorden & Model Ring
        lay_a_row1 = QHBoxLayout()
        col_renda = QVBoxLayout()
        col_renda.addWidget(QLabel("✨ Renda / Poni Gorden:"))
        self.cmb_a_renda = QComboBox()
        self.buat_combo_bisa_dicari(self.cmb_a_renda)
        col_renda.addWidget(self.cmb_a_renda)
        lay_a_row1.addLayout(col_renda)
        
        col_ring = QVBoxLayout()
        col_ring.addWidget(QLabel("⭕ Pilihan Model Ring (8 pcs/m):"))
        self.cmb_a_ring = QComboBox()
        self.buat_combo_bisa_dicari(self.cmb_a_ring)
        col_ring.addWidget(self.cmb_a_ring)
        lay_a_row1.addLayout(col_ring)
        lay_a.addLayout(lay_a_row1)
        
        # Baris 2: Tali Gorden & Hook Kaitan
        lay_a_row2 = QHBoxLayout()
        col_tali = QVBoxLayout()
        col_tali.addWidget(QLabel("🎗️ Pilihan Tali Gorden:"))
        self.cmb_a_tali = QComboBox()
        self.buat_combo_bisa_dicari(self.cmb_a_tali)
        col_tali.addWidget(self.cmb_a_tali)
        lay_a_row2.addLayout(col_tali)
        
        col_hook = QVBoxLayout()
        col_hook.addWidget(QLabel("🪝 Pilihan Hook / Kaitan:"))
        self.cmb_a_hook = QComboBox()
        self.buat_combo_bisa_dicari(self.cmb_a_hook)
        col_hook.addWidget(self.cmb_a_hook)
        lay_a_row2.addLayout(col_hook)
        lay_a.addLayout(lay_a_row2)
        
        self.layout_detail_ruang.addWidget(box_aksesoris)
        layout_konten_order.addWidget(self.grup_detail_ruang, 3)
        main_layout.addLayout(layout_konten_order)
        
        # Total Live Info
        layout_total_info = QHBoxLayout()
        layout_total_info.addStretch()
        lbl_info_teks = QLabel("TOTAL HARGA KESELURUHAN :")
        lbl_info_teks.setStyleSheet("font-size: 15px; font-weight: bold; color: white;")
        self.lbl_total_keseluruhan_rp = QLabel("Rp 0")
        self.lbl_total_keseluruhan_rp.setStyleSheet("font-size: 24px; font-weight: bold; color: #22c55e; padding-right: 10px;")
        layout_total_info.addWidget(lbl_info_teks)
        layout_total_info.addWidget(self.lbl_total_keseluruhan_rp)
        main_layout.addLayout(layout_total_info)
        
        # Tombol Simpan
        self.btn_simpan_transaksi = QPushButton("💾 SIMPAN TRANSAKSI KE DATABASE")
        self.btn_simpan_transaksi.setStyleSheet("background-color: #22c55e; color: white; padding: 12px; font-size: 14px; font-weight: bold; border-radius: 6px; border: none;")
        self.btn_simpan_transaksi.clicked.connect(self.simpan_seluruh_transaksi)
        main_layout.addWidget(self.btn_simpan_transaksi)
        
        self.hubungkan_sinyal_input_memori()
        self.tambah_ruangan_baru()

    def buat_combo_bisa_dicari(self, combo):
        # 1. Kunci kolom agar pengguna TIDAK BISA mengedit/mengetik teks manual
        combo.setEditable(False)
        
        # 2. Buat tulisan samar (Placeholder) bawaan ComboBox non-editable
        combo.setPlaceholderText("-- Pilih Barang --")
        
        # 3. Atur indeks awal ke -1 agar saat aplikasi dibuka, tulisan samar langsung muncul
        combo.setCurrentIndex(-1)

    def muat_pilihan_barang(self):
        self.ambil_master_barang_db()
        self.pindah_halaman_ruangan(self.index_ruangan_aktif)

    def get_db_path(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "database", "database.db")

    def ambil_master_barang_db(self):
        temp_master = {
            "Gorden": ["-- Pilih Barang --"], 
            "Vitrase": ["-- Pilih Barang --"], 
            "Aksesoris": ["-- Pilih Barang --"]
        }
        temp_harga = {"-- Pilih Barang --": 0, "": 0}
        
        try:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            
            try:
                cursor.execute("PRAGMA table_info(barang)")
                kolom_tersedia = [k[1] for k in cursor.fetchall()]
                
                if kolom_tersedia:
                    kol_nama = "nama" if "nama" in kolom_tersedia else ("nama_barang" if "nama_barang" in kolom_tersedia else None)
                    kol_kat = "kategori" if "kategori" in kolom_tersedia else ("kategori_barang" if "kategori_barang" in kolom_tersedia else None)
                    kol_harga = "harga" if "harga" in kolom_tersedia else ("harga_barang" if "harga_barang" in kolom_tersedia else None)
                    
                    if kol_nama and kol_kat and kol_harga:
                        cursor.execute(f"SELECT {kol_nama}, {kol_kat}, {kol_harga} FROM barang")
                        rows = cursor.fetchall()
                        for nama, kategori, harga in rows:
                            kat_clean = str(kategori).strip().capitalize()
                            if kat_clean not in ["Gorden", "Vitrase", "Aksesoris"]:
                                kat_clean = "Aksesoris"
                                
                            if nama not in temp_master[kat_clean]:
                                temp_master[kat_clean].append(nama)
                            try:
                                harga_clean = str(harga).replace(".", "").strip()
                                temp_harga[nama] = int(harga_clean)
                            except ValueError:
                                temp_harga[nama] = 0
            except sqlite3.OperationalError:
                pass
                
            conn.close()
        except Exception as e:
            print(f"Error DB Dashboard: {str(e)}")
            
        self.master_barang = temp_master
        self.harga_barang_map.update(temp_harga)

    def isi_dropdown_barang(self):
        self.putus_atau_sambung_sinyal_input(buka=False)
        
        self.cmb_g_tipe.clear(); self.cmb_g_tipe.addItems(self.master_barang["Gorden"])
        self.cmb_v_tipe.clear(); self.cmb_v_tipe.addItems(self.master_barang["Vitrase"])
        
        self.cmb_a_batang.clear(); self.cmb_a_batang.addItems(self.master_barang["Aksesoris"])
        self.cmb_a_batang_vitrase.clear(); self.cmb_a_batang_vitrase.addItems(self.master_barang["Aksesoris"])
        self.cmb_a_renda.clear(); self.cmb_a_renda.addItems(self.master_barang["Aksesoris"])
        self.cmb_a_ring.clear(); self.cmb_a_ring.addItems(self.master_barang["Aksesoris"])
        self.cmb_a_tali.clear(); self.cmb_a_tali.addItems(self.master_barang["Aksesoris"])
        self.cmb_a_hook.clear(); self.cmb_a_hook.addItems(self.master_barang["Aksesoris"])
        
        self.putus_atau_sambung_sinyal_input(buka=True)

    def tambah_ruangan_baru(self):
        id_baru = len(self.list_ruangan_input)
        self.list_ruangan_input.append({
            "nama_ruang": f"Ruangan {id_baru + 1}",
            "g_l": "", "g_t": "", "g_tipe": "-- Pilih Barang --",
            "v_l": "", "v_t": "", "v_tipe": "-- Pilih Barang --",
            "a_batang": "-- Pilih Barang --", "a_batang_v": "-- Pilih Barang --", "a_renda": "-- Pilih Barang --",
            "a_ring": "-- Pilih Barang --", "a_tali": "-- Pilih Barang --", "a_hook": "-- Pilih Barang --"
        })
        self.render_ulang_navigasi_kiri()
        self.pindah_halaman_ruangan(id_baru)

    def hapus_ruangan_aktif(self):
        if len(self.list_ruangan_input) <= 1: return
        self.list_ruangan_input.pop(self.index_ruangan_aktif)
        self.index_ruangan_aktif = max(0, self.index_ruangan_aktif - 1)
        self.render_ulang_navigasi_kiri()
        self.pindah_halaman_ruangan(self.index_ruangan_aktif)

    def render_ulang_navigasi_kiri(self):
        for i in reversed(range(self.layout_list_tombol_ruang.count())):
            item = self.layout_list_tombol_ruang.itemAt(i)
            if item and item.widget(): item.widget().setParent(None)
        for idx, data in enumerate(self.list_ruangan_input):
            lbl = ClickableLabel(idx, f"🔸 {data['nama_ruang']}")
            lbl.setStyleSheet(f"background-color: {'#4f46e5' if idx == self.index_ruangan_aktif else '#1f2937'}; color: white; padding: 10px; border-radius: 5px;")
            lbl.clicked.connect(self.pindah_halaman_ruangan)
            self.layout_list_tombol_ruang.addWidget(lbl)

    def pindah_halaman_ruangan(self, index_tujuan):
        if index_tujuan >= len(self.list_ruangan_input): return
        self.index_ruangan_aktif = index_tujuan
        self.render_ulang_navigasi_kiri()
        data = self.list_ruangan_input[index_tujuan]
        
        self.putus_atau_sambung_sinyal_input(buka=False)
        self.isi_dropdown_barang()
        self.input_nama_ruang_detail.setText(data["nama_ruang"])
        self.inp_g_l.setText(data["g_l"]); self.inp_g_t.setText(data["g_t"]); self.cmb_g_tipe.setCurrentText(data["g_tipe"])
        self.inp_v_l.setText(data["v_l"]); self.inp_v_t.setText(data["v_t"]); self.cmb_v_tipe.setCurrentText(data["v_tipe"])
        
        self.cmb_a_batang.setCurrentText(data["a_batang"])
        self.cmb_a_batang_vitrase.setCurrentText(data.get("a_batang_v", "-- Pilih Barang --"))
        self.cmb_a_renda.setCurrentText(data["a_renda"])
        self.cmb_a_ring.setCurrentText(data["a_ring"])
        self.cmb_a_tali.setCurrentText(data.get("a_tali", "-- Pilih Barang --"))
        self.cmb_a_hook.setCurrentText(data.get("a_hook", "-- Pilih Barang --"))
        
        self.putus_atau_sambung_sinyal_input(buka=True)
        self.hitung_total_harga_realtime()

    def sinkronisasi_nama_ruangan(self):
        teks = self.input_nama_ruang_detail.text().strip() or f"Ruangan {self.index_ruangan_aktif + 1}"
        self.list_ruangan_input[self.index_ruangan_aktif]["nama_ruang"] = teks
        item = self.layout_list_tombol_ruang.itemAt(self.index_ruangan_aktif).widget()
        if item: item.setText(f"🔸 {teks}")

    def simpan_form_ke_memori(self):
        if not self.list_ruangan_input or self.index_ruangan_aktif >= len(self.list_ruangan_input): return
        idx = self.index_ruangan_aktif
        self.list_ruangan_input[idx]["g_l"] = self.inp_g_l.text().strip()
        self.list_ruangan_input[idx]["g_t"] = self.inp_g_t.text().strip()
        self.list_ruangan_input[idx]["g_tipe"] = self.cmb_g_tipe.currentText()
        self.list_ruangan_input[idx]["v_l"] = self.inp_v_l.text().strip()
        self.list_ruangan_input[idx]["v_t"] = self.inp_v_t.text().strip()
        self.list_ruangan_input[idx]["v_tipe"] = self.cmb_v_tipe.currentText()
        
        self.list_ruangan_input[idx]["a_batang"] = self.cmb_a_batang.currentText()
        self.list_ruangan_input[idx]["a_batang_v"] = self.cmb_a_batang_vitrase.currentText()
        self.list_ruangan_input[idx]["a_renda"] = self.cmb_a_renda.currentText()
        self.list_ruangan_input[idx]["a_ring"] = self.cmb_a_ring.currentText()
        self.list_ruangan_input[idx]["a_tali"] = self.cmb_a_tali.currentText()
        self.list_ruangan_input[idx]["a_hook"] = self.cmb_a_hook.currentText()
        self.hitung_total_harga_realtime()

    def hitung_total_harga_realtime(self):
        total_keseluruhan = 0
        for r in self.list_ruangan_input:
            try: lebar_gorden = float(r["g_l"]) if r["g_l"] else 0.0
            except ValueError: lebar_gorden = 0.0

            try: tinggi_gorden = float(r["g_t"]) if r["g_t"] else 0.0
            except ValueError: tinggi_gorden = 0.0

            try: lebar_vitrase = float(r["v_l"]) if r["v_l"] else 0.0
            except ValueError: lebar_vitrase = 0.0

            try: tinggi_vitrase = float(r["v_t"]) if r["v_t"] else 0.0
            except ValueError: tinggi_vitrase = 0.0
            
            # 1. Kain Gorden
            if r["g_tipe"] and r["g_tipe"] != "-- Pilih Barang --":
                total_keseluruhan += int(lebar_gorden * tinggi_gorden * self.harga_barang_map.get(r["g_tipe"], 0))
            
            # 2. Kain Vitrase
            if r["v_tipe"] and r["v_tipe"] != "-- Pilih Barang --" and lebar_vitrase > 0 and tinggi_vitrase > 0:
                total_keseluruhan += int(lebar_vitrase * tinggi_vitrase * self.harga_barang_map.get(r["v_tipe"], 0))
                
            # 3. Batangan Rel Gorden
            if r["a_batang"] and r["a_batang"] != "-- Pilih Barang --" and lebar_gorden > 0:
                panjang_rel_g = lebar_gorden + 0.2  
                total_keseluruhan += int(panjang_rel_g * self.harga_barang_map.get(r["a_batang"], 0))
            
            # 4. Batangan Rel Vitrase
            a_batang_v = r.get("a_batang_v", "-- Pilih Barang --")
            if a_batang_v and a_batang_v != "-- Pilih Barang --" and lebar_vitrase > 0:
                panjang_rel_v = lebar_vitrase + 0.2
                total_keseluruhan += int(panjang_rel_v * self.harga_barang_map.get(a_batang_v, 0))
            
            # 5. Renda Gorden
            if r["a_renda"] and r["a_renda"] != "-- Pilih Barang --":
                total_keseluruhan += int(lebar_gorden * self.harga_barang_map.get(r["a_renda"], 0))
                
            # 6. Ring Gorden
            if r["a_ring"] and r["a_ring"] != "-- Pilih Barang --":
                total_keseluruhan += int(lebar_gorden * 8 * self.harga_barang_map.get(r["a_ring"], 0))
                
            # 7. Tali Gorden
            a_tali = r.get("a_tali", "-- Pilih Barang --")
            if a_tali and a_tali != "-- Pilih Barang --":
                total_keseluruhan += int(2 * self.harga_barang_map.get(a_tali, 0))
                
            # 8. Hook Kaitan
            a_hook = r.get("a_hook", "-- Pilih Barang --")
            if a_hook and a_hook != "-- Pilih Barang --":
                total_keseluruhan += int(2 * self.harga_barang_map.get(a_hook, 0))
                
        self.lbl_total_keseluruhan_rp.setText(f"Rp {total_keseluruhan:,}".replace(",", "."))
        return total_keseluruhan

    def hubungkan_sinyal_input_memori(self):
        self.inp_g_l.textChanged.connect(self.simpan_form_ke_memori)
        self.inp_g_t.textChanged.connect(self.simpan_form_ke_memori)
        self.cmb_g_tipe.currentTextChanged.connect(self.simpan_form_ke_memori)
        self.inp_v_l.textChanged.connect(self.simpan_form_ke_memori)
        self.inp_v_t.textChanged.connect(self.simpan_form_ke_memori)
        self.cmb_v_tipe.currentTextChanged.connect(self.simpan_form_ke_memori)
        
        self.cmb_a_batang.currentTextChanged.connect(self.simpan_form_ke_memori)
        self.cmb_a_batang_vitrase.currentTextChanged.connect(self.simpan_form_ke_memori)
        self.cmb_a_renda.currentTextChanged.connect(self.simpan_form_ke_memori)
        self.cmb_a_ring.currentTextChanged.connect(self.simpan_form_ke_memori)
        self.cmb_a_tali.currentTextChanged.connect(self.simpan_form_ke_memori)
        self.cmb_a_hook.currentTextChanged.connect(self.simpan_form_ke_memori)

    def putus_atau_sambung_sinyal_input(self, buka=True):
        if buka: self.hubungkan_sinyal_input_memori()
        else:
            try:
                self.inp_g_l.textChanged.disconnect(self.simpan_form_ke_memori)
                self.inp_g_t.textChanged.disconnect(self.simpan_form_ke_memori)
                self.cmb_g_tipe.currentTextChanged.disconnect(self.simpan_form_ke_memori)
                self.inp_v_l.textChanged.disconnect(self.simpan_form_ke_memori)
                self.inp_v_t.textChanged.disconnect(self.simpan_form_ke_memori)
                self.cmb_v_tipe.currentTextChanged.disconnect(self.simpan_form_ke_memori)
                
                self.cmb_a_batang.currentTextChanged.disconnect(self.simpan_form_ke_memori)
                self.cmb_a_batang_vitrase.currentTextChanged.disconnect(self.simpan_form_ke_memori)
                self.cmb_a_renda.currentTextChanged.disconnect(self.simpan_form_ke_memori)
                self.cmb_a_ring.currentTextChanged.disconnect(self.simpan_form_ke_memori)
                self.cmb_a_tali.currentTextChanged.disconnect(self.simpan_form_ke_memori)
                self.cmb_a_hook.currentTextChanged.disconnect(self.simpan_form_ke_memori)
            except TypeError: pass

    def simpan_seluruh_transaksi(self):
        nama_pembeli = self.input_nama.text().strip()
        if not nama_pembeli:
            QMessageBox.warning(self, "Data Kurang", "Nama pembeli wajib diisi!")
            return
            
        self.ambil_master_barang_db()
        total_bayar = self.hitung_total_harga_realtime()
        
        try:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pesanan (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama_pembeli TEXT,
                    no_hp TEXT,
                    alamat TEXT,
                    total_bayar INTEGER DEFAULT 0,
                    tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            try: cursor.execute("ALTER TABLE pesanan ADD COLUMN total_bayar INTEGER DEFAULT 0")
            except sqlite3.OperationalError: pass
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pesanan_detail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_pesanan INTEGER,
                    nama_ruangan TEXT,
                    gorden_lebar REAL DEFAULT 0.0,
                    gorden_tinggi REAL DEFAULT 0.0,
                    gorden_tipe TEXT,
                    vitrase_lebar REAL DEFAULT 0.0,
                    vitrase_tinggi REAL DEFAULT 0.0,
                    vitrase_tipe TEXT,
                    aksesoris_batangan TEXT,
                    aksesoris_renda TEXT,
                    aksesoris_ring TEXT,
                    aksesoris_tali_hook TEXT
                )
            """)
            
            kolom_wajib = [
                ("gorden_lebar", "REAL DEFAULT 0.0"), ("gorden_tinggi", "REAL DEFAULT 0.0"), ("gorden_tipe", "TEXT"),
                ("vitrase_lebar", "REAL DEFAULT 0.0"), ("vitrase_tinggi", "REAL DEFAULT 0.0"), ("vitrase_tipe", "TEXT"),
                ("aksesoris_batangan", "TEXT"), ("aksesoris_renda", "TEXT"), ("aksesoris_ring", "TEXT"), ("aksesoris_tali_hook", "TEXT")
            ]
            for nama_kol, tipe_kol in kolom_wajib:
                try: cursor.execute(f"ALTER TABLE pesanan_detail ADD COLUMN {nama_kol} {tipe_kol}")
                except sqlite3.OperationalError: pass
                
            cursor.execute("""
                INSERT INTO pesanan (nama_pembeli, no_hp, alamat, total_bayar) 
                VALUES (?, ?, ?, ?)
            """, (nama_pembeli, self.input_hp.text().strip(), self.input_alamat.text().strip(), total_bayar))
            
            id_pesanan_baru = cursor.lastrowid
            
            for r in self.list_ruangan_input:
                try: g_l = float(r.get("g_l", "")) if r.get("g_l") else 0.0
                except ValueError: g_l = 0.0
                try: g_t = float(r.get("g_t", "")) if r.get("g_t") else 0.0
                except ValueError: g_t = 0.0
                try: v_l = float(r.get("v_l", "")) if r.get("v_l") else 0.0
                except ValueError: v_l = 0.0
                try: v_t = float(r.get("v_t", "")) if r.get("v_t") else 0.0
                except ValueError: v_t = 0.0

                nama_ruang = r.get("nama_ruang", "Ruangan")
                g_tipe = r.get("g_tipe", "-- Pilih Barang --")
                v_tipe = r.get("v_tipe", "-- Pilih Barang --")
                a_batang = r.get("a_batang", "-- Pilih Barang --")
                a_renda = r.get("a_renda", "-- Pilih Barang --")
                a_ring = r.get("a_ring", "-- Pilih Barang --")

                str_batang = f"Gorden: {a_batang} | Vitrase: {r.get('a_batang_v', '-- Pilih Barang --')}"
                str_tali_hook = f"Tali: {r.get('a_tali', '-- Pilih Barang --')} | Hook: {r.get('a_hook', '-- Pilih Barang --')}"
                
                cursor.execute("""
                    INSERT INTO pesanan_detail (
                        id_pesanan, nama_ruangan, 
                        gorden_lebar, gorden_tinggi, gorden_tipe, 
                        vitrase_lebar, vitrase_tinggi, vitrase_tipe, 
                        aksesoris_batangan, aksesoris_renda, aksesoris_ring, aksesoris_tali_hook
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id_pesanan_baru, nama_ruang,
                    g_l, g_t, g_tipe,
                    v_l, v_t, v_tipe,
                    str_batang, a_renda, a_ring, str_tali_hook
                ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Pesanan Berhasil", f"Data pesanan & rincian ruangan untuk {nama_pembeli} sukses disimpan ke database!")
            
            self.input_nama.clear(); self.input_hp.clear(); self.input_alamat.clear()
            self.list_ruangan_input = []; self.index_ruangan_aktif = 0; self.tambah_ruangan_baru()

            self.transaksi_disimpan.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Error Database", f"Gagal menyimpan transaksi ke database:\n{str(e)}")