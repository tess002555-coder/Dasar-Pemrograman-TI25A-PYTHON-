from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QLineEdit, QPushButton, QFormLayout, QComboBox, QMessageBox, QMenu, QFileDialog)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction
import sqlite3
import os
import pandas as pd  # Pastikan sudah menginstall: pip install pandas openpyxl

class DataBarang(QWidget):
    def __init__(self):
        super().__init__()
        
        # Variabel pembantu untuk menyimpan ID barang yang sedang diedit
        self.id_barang_diedit = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # --- Judul Halaman ---
        title = QLabel("MANAJEMEN DATA STOK & HARGA BARANG")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #a78bfa; margin-bottom: 5px; letter-spacing: 1px;")
        layout.addWidget(title)
        
        # --- Form Input Barang Baru ---
        grup_input = QWidget()
        grup_input.setStyleSheet("""
            QLabel { color: #e5e7eb; font-size: 13px; font-weight: bold; }
            QLineEdit, QComboBox { background-color: #1f2937; color: white; border: 1px solid #374151; padding: 8px; border-radius: 6px; }
            QLineEdit:focus, QComboBox:focus { border-color: #a78bfa; }
        """)
        
        form_layout = QFormLayout(grup_input)
        form_layout.setSpacing(10)
        
        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Misal: Rel Alumunium Double, Kain Blackout Premium...")
        
        self.combo_kategori = QComboBox()
        self.combo_kategori.addItems(["Gorden", "Vitrase", "Batangan", "Aksesoris"])
        
        self.input_harga = QLineEdit()
        self.input_harga.setPlaceholderText("Masukkan harga angka saja (Misal: 50000)...")
        
        form_layout.addRow("Nama Barang / Paket:", self.input_nama)
        form_layout.addRow("Kategori Produk:", self.combo_kategori)
        form_layout.addRow("Harga (Rp):", self.input_harga)
        layout.addWidget(grup_input)
        
        # --- Tombol Aksi ---
        self.layout_tombol = QHBoxLayout()
        
        self.btn_tambah = QPushButton("➕ Tambah Barang Baru")
        self.btn_tambah.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tambah.setStyleSheet("""
            QPushButton { background-color: #2563eb; color: white; padding: 10px; font-weight: bold; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_tambah.clicked.connect(self.proses_simpan_barang)
        
        # Tombol Batal Edit (Awalnya disembunyikan)
        self.btn_batal = QPushButton("❌ Batal Edit")
        self.btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batal.setStyleSheet("""
            QPushButton { background-color: #ef4444; color: white; padding: 10px; font-weight: bold; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #dc2626; }
        """)
        self.btn_batal.clicked.connect(self.reset_ke_mode_tambah)
        self.btn_batal.hide()
        
        # Tombol Import Excel (.xlsx)
        self.btn_import = QPushButton("📁 Import Massal (.xlsx)")
        self.btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_import.setStyleSheet("""
            QPushButton { background-color: #059669; color: white; padding: 10px; font-weight: bold; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #047857; }
        """)
        self.btn_import.clicked.connect(self.import_excel)
        
        self.layout_tombol.addWidget(self.btn_tambah)
        self.layout_tombol.addWidget(self.btn_batal)
        self.layout_tombol.addWidget(self.btn_import)
        layout.addLayout(self.layout_tombol)
        
        # --- Tabel Data Master Barang ---
        self.tabel = QTableWidget()
        self.tabel.setColumnCount(3)
        self.tabel.setHorizontalHeaderLabels(["Nama Barang", "Kategori", "Harga Per Meter / Pcs"])
        self.tabel.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Penempatan Label "No" di Pojok Kiri Atas secara Akurat
        self.tabel.setCornerButtonEnabled(False)
        self.lbl_corner = QLabel("No", self.tabel)
        self.lbl_corner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_corner.setStyleSheet("""
            background-color: #1f2937; 
            color: #a78bfa; 
            font-weight: bold; 
            font-size: 13px;
            border-right: 1px solid #374151;
            border-bottom: 1px solid #374151;
        """)
        
        self.tabel.horizontalHeader().geometriesChanged.connect(self.sinkronisasi_posisi_no)
        self.tabel.verticalHeader().geometriesChanged.connect(self.sinkronisasi_posisi_no)
        
        # Style Header No Urut Samping
        self.tabel.verticalHeader().setStyleSheet("background-color: #1f2937; color: #9ca3af; font-weight: bold;")
        self.tabel.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabel.verticalHeader().setFixedWidth(45)
        
        # Seleksi 1 Baris & Hilangkan Kotak Fokus Putih
        self.tabel.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabel.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabel.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Menu Klik Kanan
        self.tabel.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabel.customContextMenuRequested.connect(self.buka_menu_klik_kanan)
        
        self.tabel.setStyleSheet("""
            QTableWidget { background-color: #111827; color: white; gridline-color: #374151; border: 1px solid #374151; border-radius: 6px; font-size: 13px; }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #1f2937; }
            QHeaderView::section { background-color: #1f2937; color: #a78bfa; font-weight: bold; padding: 8px; border: 1px solid #374151; }
            QTableWidget::item:selected { background-color: #4f46e5; color: white; }
        """)
        layout.addWidget(self.tabel)
        
        self.load_data()

    def sinkronisasi_posisi_no(self):
        w = self.tabel.verticalHeader().width()
        h = self.tabel.horizontalHeader().height()
        self.lbl_corner.setGeometry(0, 0, w, h)

    def get_db_path(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "database", "database.db")
        if not os.path.exists(os.path.dirname(db_path)):
            return "kasir_gorden.db"
        return db_path

    def load_data(self):
        try:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS barang (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    nama_barang TEXT NOT NULL, 
                    kategori TEXT NOT NULL, 
                    harga TEXT NOT NULL
                )
            """)
            cursor.execute("SELECT id, nama_barang, kategori, harga FROM barang ORDER BY id DESC")
            data = cursor.fetchall()
            conn.close()
            
            self.tabel.setRowCount(0)
            for row_idx, (id_barang, nama, kategori, harga) in enumerate(data):
                self.tabel.insertRow(row_idx)
                self.tabel.setVerticalHeaderItem(row_idx, QTableWidgetItem(str(row_idx + 1)))
                
                item_nama = QTableWidgetItem(nama)
                item_nama.setData(Qt.ItemDataRole.UserRole, id_barang)
                item_kategori = QTableWidgetItem(kategori)
                
                try:
                    harga_formatted = f"Rp {int(harga):,}".replace(",", ".")
                except ValueError:
                    harga_formatted = f"Rp {harga}"
                item_harga = QTableWidgetItem(harga_formatted)
                
                for item in [item_nama, item_kategori, item_harga]:
                    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                
                self.tabel.setItem(row_idx, 0, item_nama)
                self.tabel.setItem(row_idx, 1, item_kategori)
                self.tabel.setItem(row_idx, 2, item_harga)
                
        except Exception as e:
            print(f"Error load data: {str(e)}")

    def proses_simpan_barang(self):
        nama = self.input_nama.text().strip()
        kategori = self.combo_kategori.currentText()
        harga_raw = self.input_harga.text().strip()
        
        if not nama or not harga_raw:
            QMessageBox.warning(self, "Input Kosong", "Kolom nama dan harga wajib diisi!")
            return
            
        try:
            harga_clean = harga_raw.replace("Rp", "").replace(".", "").replace(",", "").strip()
            harga = int(harga_clean)
        except ValueError:
            QMessageBox.warning(self, "Salah Input", "Harga harus berupa angka murni!")
            return
            
        try:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            
            if self.id_barang_diedit is None:
                cursor.execute("INSERT INTO barang (nama_barang, kategori, harga) VALUES (?, ?, ?)", (nama, kategori, str(harga)))
                QMessageBox.information(self, "Berhasil", "Data barang baru berhasil ditambahkan!")
            else:
                cursor.execute("UPDATE barang SET nama_barang=?, kategori=?, harga=? WHERE id=?", (nama, kategori, str(harga), self.id_barang_diedit))
                QMessageBox.information(self, "Berhasil", "Perubahan data barang sukses disimpan!")
                self.reset_ke_mode_tambah()
                
            conn.commit()
            conn.close()
            
            self.input_nama.clear()
            self.input_harga.clear()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal menyimpan data: {str(e)}")

    def reset_ke_mode_tambah(self):
        """ Mengembalikan form ke keadaan input baru semula """
        self.id_barang_diedit = None
        self.input_nama.clear()
        self.input_harga.clear()
        self.combo_kategori.setCurrentIndex(0)
        
        self.btn_tambah.setText("➕ Tambah Barang Baru")
        self.btn_tambah.setStyleSheet("""
            QPushButton { background-color: #2563eb; color: white; padding: 10px; font-weight: bold; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_batal.hide()

    def import_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih File Excel Data Barang", "", "Excel Files (*.xlsx *.xls)")
        if not file_path:
            return
            
        try:
            df = pd.read_excel(file_path)
            
            # Membersihkan spasi gaib di nama kolom Excel dan mengubahnya ke huruf kecil semua
            df.columns = df.columns.str.strip().str.lower()
            
            # Pengecekan versi toleran (menggunakan huruf kecil)
            kolom_wajib = ["nama barang", "kategori", "harga"]
            for col in kolom_wajib:
                if col not in df.columns:
                    QMessageBox.critical(
                        self, "Format Salah", 
                        "Format Excel kurang pas!\n\nPastikan baris pertama Excel Anda memiliki kolom dengan nama:\n"
                        "- Nama Barang\n- Kategori\n- Harga"
                    )
                    return
            
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            
            jumlah_sukses = 0
            for _, row in df.iterrows():
                # Mengambil data menggunakan nama kolom huruf kecil
                nama = str(row["nama barang"]).strip()
                kategori = str(row["kategori"]).strip()
                
                # Membersihkan value harga jika ada desimal float dari excel (.0)
                harga_raw = str(row["harga"]).split('.')[0]
                harga_clean = ''.join(filter(str.isdigit, harga_raw))
                
                if nama and kategori and harga_clean:
                    cursor.execute("INSERT INTO barang (nama_barang, kategori, harga) VALUES (?, ?, ?)", 
                                   (nama, kategori, harga_clean))
                    jumlah_sukses += 1
            
            conn.commit()
            conn.close()
            
            self.load_data()
            QMessageBox.information(self, "Berhasil", f"Sukses mengimport {jumlah_sukses} data barang dari Excel!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error Import", f"Gagal membaca file Excel:\n{str(e)}")

    def buka_menu_klik_kanan(self, posisi: QPoint):
        index_tabel = self.tabel.indexAt(posisi)
        # PERBAIKAN: Memisahkan pengecekan validasi agar tidak memicu SyntaxError
        if not index_tabel.isValid(): 
            return
            
        row = index_tabel.row()
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #1f2937; color: white; border: 1px solid #374151; padding: 4px; }
            QMenu::item { padding: 6px 20px; border-radius: 4px; }
            QMenu::item:selected { background-color: #4f46e5; }
        """)
        
        aksi_edit = QAction("✏️ Edit Produk (Lempar ke Form)", self)
        aksi_edit.triggered.connect(lambda: self.siapkan_edit_form(row))
        
        aksi_hapus = QAction("🗑 Hapus Produk Ini", self)
        aksi_hapus.triggered.connect(lambda: self.hapus_barang_proses(row))
        
        menu.addAction(aksi_edit)
        menu.addSeparator()
        menu.addAction(aksi_hapus)
        
        menu.exec(self.tabel.viewport().mapToGlobal(posisi))

    def siapkan_edit_form(self, row):
        item_nama = self.tabel.item(row, 0)
        item_kategori = self.tabel.item(row, 1)
        item_harga = self.tabel.item(row, 2)
        
        self.id_barang_diedit = item_nama.data(Qt.ItemDataRole.UserRole)
        
        self.input_nama.setText(item_nama.text())
        index_kategori = self.combo_kategori.findText(item_kategori.text())
        if index_kategori >= 0:
            self.combo_kategori.setCurrentIndex(index_kategori)
            
        harga_clean = item_harga.text().replace("Rp", "").replace(".", "").replace(",", "").strip()
        self.input_harga.setText(harga_clean)
        
        # Ubah Tombol Utama dan Munculkan Tombol Batal
        self.btn_tambah.setText("💾 Simpan Perubahan Barang")
        self.btn_tambah.setStyleSheet("""
            QPushButton { background-color: #d97706; color: white; padding: 10px; font-weight: bold; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #b45309; }
        """)
        self.btn_batal.show()

    def hapus_barang_proses(self, row):
        item_nama = self.tabel.item(row, 0)
        id_barang = item_nama.data(Qt.ItemDataRole.UserRole)
        nama_produk = item_nama.text()
        
        konfirmasi = QMessageBox.question(
            self, "Hapus Produk", f"Apakah Anda yakin ingin menghapus produk '{nama_produk}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if konfirmasi == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect(self.get_db_path())
                cursor = conn.cursor()
                cursor.execute("DELETE FROM barang WHERE id = ?", (id_barang,))
                conn.commit()
                conn.close()
                self.load_data()
                if self.id_barang_diedit == id_barang:
                    self.reset_ke_mode_tambah()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus: {str(e)}")