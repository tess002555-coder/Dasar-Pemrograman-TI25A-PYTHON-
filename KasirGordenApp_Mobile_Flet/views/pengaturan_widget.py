from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QTextEdit, QPushButton, QFormLayout, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import sqlite3
import os
import shutil

class PengaturanWidget(QWidget):  # Nama kelas disesuaikan dengan nama file Anda
    def __init__(self):
        super().__init__()
        
        self.logo_path_temp = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # --- Judul Halaman ---
        title = QLabel("PENGATURAN SISTEM APLIKASI")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #a78bfa; letter-spacing: 1px;")
        layout.addWidget(title)
        
        style_grup = """
            QWidget#Grup { 
                background-color: #1f2937; 
                border-radius: 8px; 
                padding: 15px;
            }
            QLabel { color: #e5e7eb; font-size: 13px; font-weight: bold; }
            QLineEdit, QTextEdit { background-color: #111827; color: white; border: 1px solid #374151; padding: 8px; border-radius: 6px; }
            QLineEdit:focus, QTextEdit:focus { border-color: #a78bfa; }
        """
        
        # --- KELOMPOK 1: PROFIL & LOGO TOKO ---
        lbl_sec1 = QLabel("🏢 PROFIL & IDENTITAS TOKO")
        lbl_sec1.setStyleSheet("color: #a78bfa; font-weight: bold; font-size: 14px;")
        layout.addWidget(lbl_sec1)
        
        grup_toko = QWidget()
        grup_toko.setObjectName("Grup")
        grup_toko.setStyleSheet(style_grup)
        
        layout_toko_horizontal = QHBoxLayout(grup_toko)
        
        widget_form = QWidget()
        form_toko = QFormLayout(widget_form)
        form_toko.setContentsMargins(0, 0, 0, 0)
        
        self.input_nama_toko = QLineEdit()
        self.input_nama_toko.setPlaceholderText("Contoh: Berkah Gorden")
        
        self.input_alamat = QLineEdit()
        self.input_alamat.setPlaceholderText("Jl. Raya No. 123...")
        
        self.input_kontak = QLineEdit()
        self.input_kontak.setPlaceholderText("081234567xxx")
        
        form_toko.addRow("Nama Toko:", self.input_nama_toko)
        form_toko.addRow("Alamat Lengkap:", self.input_alamat)
        form_toko.addRow("No. HP / WhatsApp:", self.input_kontak)
        layout_toko_horizontal.addWidget(widget_form, stretch=3)
        
        widget_logo = QWidget()
        layout_logo = QVBoxLayout(widget_logo)
        layout_logo.setContentsMargins(10, 0, 0, 0)
        layout_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_preview_logo = QLabel("Belum Ada Logo")
        self.lbl_preview_logo.setFixedSize(90, 90)
        self.lbl_preview_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview_logo.setStyleSheet("border: 2px dashed #4b5563; border-radius: 8px; color: #9ca3af; font-size: 11px; background-color: #111827;")
        
        self.btn_pilih_logo = QPushButton("🖼️ Pilih Logo")
        self.btn_pilih_logo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pilih_logo.setStyleSheet("background-color: #4b5563; color: white; padding: 5px 10px; font-size: 11px; font-weight: bold; border-radius: 4px; border: none;")
        self.btn_pilih_logo.clicked.connect(self.pilih_gambar_logo)
        
        layout_logo.addWidget(self.lbl_preview_logo)
        layout_logo.addWidget(self.btn_pilih_logo)
        layout_toko_horizontal.addWidget(widget_logo, stretch=1)
        
        layout.addWidget(grup_toko)
        
        # --- KELOMPOK 2: KEBIJAKAN NOTA ---
        lbl_sec2 = QLabel("📄 LAYOUT & SYARAT NOTA")
        lbl_sec2.setStyleSheet("color: #a78bfa; font-weight: bold; font-size: 14px;")
        layout.addWidget(lbl_sec2)
        
        grup_nota = QWidget()
        grup_nota.setObjectName("Grup")
        grup_nota.setStyleSheet(style_grup)
        form_nota = QFormLayout(grup_nota)
        
        self.input_footer_nota = QTextEdit()
        self.input_footer_nota.setPlaceholderText("Tulis catatan kaki di sini...")
        self.input_footer_nota.setMaximumHeight(80)
        
        form_nota.addRow("Catatan Kaki Struk (Footer):", self.input_footer_nota)
        layout.addWidget(grup_nota)
        
        # --- KELOMPOK 2.5: KEAMANAN & AKSES LOGIN ---
        lbl_sec_login = QLabel("🔑 KEAMANAN & AKSES LOGIN")
        lbl_sec_login.setStyleSheet("color: #a78bfa; font-weight: bold; font-size: 14px;")
        layout.addWidget(lbl_sec_login)
        
        grup_login = QWidget()
        grup_login.setObjectName("Grup")
        grup_login.setStyleSheet(style_grup)
        form_login = QFormLayout(grup_login)
        
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Masukkan username (kosongkan jika tidak ingin login)...")
        
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Masukkan password (kosongkan jika tidak ingin login)...")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_login.addRow("Username Login:", self.input_username)
        form_login.addRow("Password Login:", self.input_password)
        layout.addWidget(grup_login)
        
        # --- KELOMPOK 3: DATABASE & MAINTENANCE ---
        lbl_sec3 = QLabel("💾 MAINTENANCE DATABASE")
        lbl_sec3.setStyleSheet("color: #a78bfa; font-weight: bold; font-size: 14px;")
        layout.addWidget(lbl_sec3)
        
        grup_db = QWidget()
        grup_db.setObjectName("Grup")
        grup_db.setStyleSheet(style_grup)
        layout_db = QHBoxLayout(grup_db)
        
        self.btn_backup = QPushButton("📦 Backup Database")
        self.btn_backup.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_backup.setStyleSheet("background-color: #059669; color: white; padding: 10px; font-weight: bold; border-radius: 6px; border: none;")
        self.btn_backup.clicked.connect(self.proses_backup)
        
        self.btn_restore = QPushButton("🔄 Restore Database")
        self.btn_restore.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restore.setStyleSheet("background-color: #d97706; color: white; padding: 10px; font-weight: bold; border-radius: 6px; border: none;")
        self.btn_restore.clicked.connect(self.proses_restore)
        
        layout_db.addWidget(self.btn_backup)
        layout_db.addWidget(self.btn_restore)
        layout.addWidget(grup_db)
        
        # --- TOMBOL UTAMA SIMPAN ---
        self.btn_simpan_config = QPushButton("💾 Simpan Semua Pengaturan")
        self.btn_simpan_config.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simpan_config.setStyleSheet("""
            QPushButton { background-color: #2563eb; color: white; padding: 12px; font-size: 14px; font-weight: bold; border-radius: 6px; border: none; margin-top: 10px;}
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_simpan_config.clicked.connect(self.simpan_pengaturan)
        layout.addWidget(self.btn_simpan_config)
        
        layout.addStretch()
        self.load_pengaturan()

    def get_db_path(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "database", "database.db")

    def pilih_gambar_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih Gambar Logo Toko", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            pixmap = QPixmap(file_path)
            self.lbl_preview_logo.setPixmap(pixmap.scaled(self.lbl_preview_logo.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.lbl_preview_logo.setText("")
            self.logo_path_temp = file_path

    def load_pengaturan(self):
        try:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS login_admin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            cursor.execute("SELECT username, password FROM login_admin LIMIT 1")
            row = cursor.fetchone()
            if row:
                self.input_username.setText(row[0])
                self.input_password.setText(row[1])
            conn.close()
        except Exception as e:
            print(f"Gagal memuat pengaturan login: {e}")

    def simpan_pengaturan(self):
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()
        
        try:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS login_admin (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            
            # Hapus data login yang lama
            cursor.execute("DELETE FROM login_admin")
            
            # Jika user menginputkan username dan password, simpan
            if username and password:
                cursor.execute("INSERT INTO login_admin (username, password) VALUES (?, ?)", (username, password))
                QMessageBox.information(self, "Berhasil", "Username & Password login berhasil diaktifkan / diperbarui!")
            else:
                QMessageBox.information(self, "Berhasil", "Pengaturan disimpan. Login dinonaktifkan karena username/password kosong.")
                
            conn.commit()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan pengaturan login: {str(e)}")

    def proses_backup(self):
        try:
            db_asal = self.get_db_path()
            if not os.path.exists(db_asal):
                QMessageBox.warning(self, "Gagal", "Database utama tidak ditemukan!")
                return
            folder_tujuan = QFileDialog.getExistingDirectory(self, "Pilih Folder Simpan Backup")
            if folder_tujuan:
                shutil.copy(db_asal, os.path.join(folder_tujuan, "backup_kasir_gorden.db"))
                QMessageBox.information(self, "Backup Sukses", "Salinan database berhasil disimpan!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal backup: {str(e)}")

    def proses_restore(self):
        try:
            file_backup, _ = QFileDialog.getOpenFileName(self, "Pilih File Backup Database", "", "Database Files (*.db)")
            if file_backup:
                konfirmasi = QMessageBox.question(
                    self, "Konfirmasi Restore", "Proses restore akan menimpa data transaksi saat ini. Lanjutkan?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if konfirmasi == QMessageBox.StandardButton.Yes:
                    db_tujuan = self.get_db_path()
                    shutil.copy(file_backup, db_tujuan)
                    QMessageBox.information(self, "Restore Sukses", "Database berhasil dikembalikan! Silakan restart aplikasi.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal restore: {str(e)}")