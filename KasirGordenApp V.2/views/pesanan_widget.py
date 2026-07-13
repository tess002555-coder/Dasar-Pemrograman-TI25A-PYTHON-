import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QMessageBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt

class FormRuanganWidget(QFrame):
    """Widget untuk input detail per ruangan"""
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        layout = QVBoxLayout(self)
        
        self.input_tempat = QLineEdit()
        self.input_tempat.setPlaceholderText("Nama Ruangan (contoh: Kamar Utama)")
        
        self.combo_kain = QComboBox()
        self.combo_vitrase = QComboBox()
        # Anda bisa menambahkan logika untuk mengisi combo box dari database
        
        layout.addWidget(QLabel("Ruangan:"))
        layout.addWidget(self.input_tempat)
        layout.addWidget(self.combo_kain)
        layout.addWidget(self.combo_vitrase)

class PesananWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.daftar_form_ruangan = []
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Nama Pembeli")
        main_layout.addWidget(self.input_nama)
        
        # Area untuk list ruangan
        self.scroll = QScrollArea()
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.scroll.setWidget(self.container)
        self.scroll.setWidgetResizable(True)
        main_layout.addWidget(self.scroll)
        
        self.btn_tambah_ruangan = QPushButton("Tambah Ruangan")
        self.btn_tambah_ruangan.clicked.connect(self.tambah_form_ruangan)
        main_layout.addWidget(self.btn_tambah_ruangan)
        
        self.lbl_total_harga = QLabel("Total: Rp 0")
        main_layout.addWidget(self.lbl_total_harga)
        
        self.btn_simpan = QPushButton("Simpan Transaksi")
        self.btn_simpan.clicked.connect(self.simpan_transaksi)
        main_layout.addWidget(self.btn_simpan)

    def tambah_form_ruangan(self):
        form = FormRuanganWidget()
        self.daftar_form_ruangan.append(form)
        self.container_layout.addWidget(form)

    def simpan_transaksi(self):
        nama = self.input_nama.text().strip()
        if not nama or not self.daftar_form_ruangan:
            QMessageBox.warning(self, "Peringatan", "Lengkapi nama dan detail ruangan!")
            return

        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            
            # Simpan Header
            cursor.execute("INSERT INTO pesanan (nama_pelanggan, total_harga) VALUES (?, ?)", (nama, 0))
            id_pesanan = cursor.lastrowid
            
            # Simpan Detail
            for form in self.daftar_form_ruangan:
                cursor.execute("""
                    INSERT INTO detail_pesanan (id_pesanan, nama_ruangan, item_barang) 
                    VALUES (?, ?, ?)
                """, (id_pesanan, form.input_tempat.text(), f"{form.combo_kain.currentText()} & {form.combo_vitrase.currentText()}"))
            
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Sukses", "Pesanan berhasil disimpan.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))