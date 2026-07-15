import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, \
    QHeaderView, QMessageBox, QFileDialog, QDialog, QFormLayout
)
from PyQt6.QtCore import Qt

class FormBarangDialog(QDialog):
    def __init__(self, parent=None, data_barang=None):
        super().__init__(parent)
        self.data_barang = data_barang 
        self.setWindowTitle("Form Data Barang" if data_barang else "Tambah Barang Baru")
        self.resize(400, 250)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        lbl_title = QLabel("EDIT DATA BARANG" if self.data_barang else "TAMBAH BARANG BARU")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #7a52cc; margin-bottom: 10px;")
        layout.addWidget(lbl_title)
        
        form_layout = QFormLayout()
        style_input = """
            QLineEdit, QComboBox { 
                background-color: #2a2a2a; 
                color: white; 
                border: 1px solid #3e3e3e; 
                padding: 6px; 
                border-radius: 4px; 
            }
        """
        
        self.input_nama = QLineEdit()
        self.input_nama.setStyleSheet(style_input)
        if self.data_barang:
            self.input_nama.setText(self.data_barang['nama'])
        form_layout.addRow("Nama Barang:", self.input_nama)
        
        self.input_kategori = QComboBox()
        self.input_kategori.addItems(["Gorden", "Vitrase", "Aksesoris"])
        self.input_kategori.setStyleSheet(style_input)
        if self.data_barang:
            self.input_kategori.setCurrentText(self.data_barang['kategori'])
        form_layout.addRow("Kategori:", self.input_kategori)
        
        self.input_harga = QLineEdit()
        self.input_harga.setStyleSheet(style_input)
        if self.data_barang:
            self.input_harga.setText(str(self.data_barang['harga']))
        form_layout.addRow("Harga / Meter:", self.input_harga)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        self.btn_simpan = QPushButton("Simpan")
        self.btn_simpan.setStyleSheet("background-color: #7a52cc; color: white; font-weight: bold; padding: 8px; border-radius: 4px;")
        self.btn_simpan.clicked.connect(self.accept)
        
        self.btn_batal = QPushButton("Batal")
        self.btn_batal.setStyleSheet("background-color: #3e3e3e; color: white; padding: 8px; border-radius: 4px;")
        self.btn_batal.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_batal)
        btn_layout.addWidget(self.btn_simpan)
        layout.addLayout(btn_layout)
        
    def get_data(self):
        return {
            "nama": self.input_nama.text(),
            "kategori": self.input_kategori.currentText(),
            "harga": self.input_harga.text()
        }

class BarangWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.muat_data_barang()
        
    def init_ui(self):
        layout_utama = QVBoxLayout(self)
        layout_utama.setContentsMargins(20, 20, 20, 20)
        layout_utama.setSpacing(15)
        
        layout_atas = QHBoxLayout()
        lbl_judul = QLabel("Manajemen Data Barang Gorden")
        lbl_judul.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        layout_atas.addWidget(lbl_judul)
        
        self.btn_tambah = QPushButton("+ Tambah Barang")
        self.btn_tambah.setStyleSheet("background-color: #7a52cc; color: white; font-weight: bold; padding: 8px 15px; border-radius: 4px;")
        self.btn_tambah.clicked.connect(self.buka_dialog_tambah)
        layout_atas.addWidget(self.btn_tambah)
        
        self.btn_impor = QPushButton("📥 Impor File")
        self.btn_impor.setStyleSheet("background-color: #2b7a78; color: white; font-weight: bold; padding: 8px 15px; border-radius: 4px;")
        self.btn_impor.clicked.connect(self.proses_impor_file)
        layout_atas.addWidget(self.btn_impor)
        
        layout_utama.addLayout(layout_atas)
        
        self.tabel = QTableWidget()
        self.tabel.setColumnCount(5)
        self.tabel.setHorizontalHeaderLabels(["ID", "Nama Barang", "Kategori", "Harga / Meter", "Aksi"])
        self.tabel.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabel.setStyleSheet("""
            QTableWidget { background-color: #1e1e1e; color: white; gridline-color: #2d2d2d; }
            QHeaderView::section { background-color: #2a2a2a; color: white; padding: 5px; }
        """)
        layout_utama.addWidget(self.tabel)

    def muat_data_barang(self):
        self.tabel.setRowCount(0)
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, nama_barang, kategori, harga_per_meter FROM barang")
            baris_data = cursor.fetchall()
            conn.close()
            
            for index_baris, data in enumerate(baris_data):
                self.tabel.insertRow(index_baris)
                self.tabel.setItem(index_baris, 0, QTableWidgetItem(str(data[0])))
                self.tabel.setItem(index_baris, 1, QTableWidgetItem(str(data[1])))
                self.tabel.setItem(index_baris, 2, QTableWidgetItem(str(data[2])))
                
                harga_format = f"Rp {int(data[3]):,}".replace(",", ".")
                self.tabel.setItem(index_baris, 3, QTableWidgetItem(harga_format))
                
                panel_tombol = QWidget()
                layout_tombol = QHBoxLayout(panel_tombol)
                layout_tombol.setContentsMargins(2, 2, 2, 2)
                layout_tombol.setSpacing(5)
                
                btn_edit = QPushButton("✏️")
                btn_edit.setStyleSheet("background-color: #e0a96d; border-radius: 3px; padding: 3px;")
                btn_edit.clicked.connect(lambda checked, b=data: self.buka_dialog_edit(b[0], b[1], b[2], b[3]))
                
                btn_hapus = QPushButton("🗑️")
                btn_hapus.setStyleSheet("background-color: #d9534f; border-radius: 3px; padding: 3px;")
                btn_hapus.clicked.connect(lambda checked, id_b=data[0]: self.hapus_data_barang(id_b))
                
                layout_tombol.addWidget(btn_edit)
                layout_tombol.addWidget(btn_hapus)
                self.tabel.setCellWidget(index_baris, 4, panel_tombol)
                
        except Exception as e:
            print("Gagal memuat data barang:", str(e))

    def proses_impor_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih File Data", "", "Format Teks (*.txt);;Semua File (*)")
        if not file_path:
            return
            
        try:
            barang_data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for baris in f:
                    baris = baris.strip()
                    if not baris or baris.startswith('#'):
                        continue
                    bagian = baris.split(',')
                    if len(bagian) == 3:
                        nama = bagian[0].strip()
                        kategori = bagian[1].strip()
                        try:
                            harga = float(bagian[2].strip())
                            barang_data.append((nama, kategori, harga))
                        except ValueError:
                            continue
            
            if barang_data:
                conn = sqlite3.connect('database.db')
                conn.executemany("INSERT INTO barang (nama_barang, kategori, harga_per_meter) VALUES (?, ?, ?)", barang_data)
                conn.commit()
                conn.close()
                self.muat_data_barang()
                QMessageBox.information(self, "Sukses", f"Berhasil mengimpor {len(barang_data)} data.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def buka_dialog_tambah(self):
        dialog = FormBarangDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            conn = sqlite3.connect('database.db')
            conn.execute("INSERT INTO barang (nama_barang, kategori, harga_per_meter) VALUES (?, ?, ?)", (data['nama'], data['kategori'], float(data['harga'])))
            conn.commit()
            conn.close()
            self.muat_data_barang()

    def buka_dialog_edit(self, id_b, nama_b, kat_b, harga_b):
        dialog = FormBarangDialog(self, data_barang={"nama": nama_b, "kategori": kat_b, "harga": harga_b})
        if dialog.exec():
            data = dialog.get_data()
            conn = sqlite3.connect('database.db')
            conn.execute("UPDATE barang SET nama_barang=?, kategori=?, harga_per_meter=? WHERE id=?", (data['nama'], data['kategori'], float(data['harga']), id_b))
            conn.commit()
            conn.close()
            self.muat_data_barang()

    def hapus_data_barang(self, id_b):
        tanya = QMessageBox.question(self, "Konfirmasi Hapus", "Apakah Anda yakin ingin menghapus barang ini?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if tanya == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect('database.db')
            conn.execute("DELETE FROM barang WHERE id=?", (id_b,))
            conn.commit()
            conn.close()
            self.muat_data_barang()