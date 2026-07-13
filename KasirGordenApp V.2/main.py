import sys
import os
import sqlite3
from PyQt6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QFrame, QLabel, QMessageBox)
from views.dashboard_input import DashboardInput
from views.riwayat_transaksi import RiwayatTransaksi
from views.data_barang import DataBarang  
from views.pengaturan_widget import PengaturanWidget
from views.login_window import LoginWindow
from database.db import init_database

class MainWindow(QWidget):
    def __init__(self, logout_callback=None):
        super().__init__()
        self.logout_callback = logout_callback
        self.setWindowTitle("KasirGordenApp")
        self.resize(1100, 750)
        
        # Hilangkan margin bawaan agar sidebar bisa menempel penuh ke tepi kiri
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ==========================================
        # --- SIDEBAR KIRI (DIPERCANTIK) ---
        # ==========================================
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFixedWidth(240)  # Kunci lebar sidebar
        self.sidebar_frame.setStyleSheet("""
            QFrame {
                background-color: #0f172a; /* Warna latar biru sangat gelap */
                border-right: 1px solid #1e293b;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(15, 30, 15, 25)
        sidebar_layout.setSpacing(12)
        
        # 1. Judul / Logo Aplikasi di Sidebar
        lbl_app_name = QLabel("✨ KasirGorden")
        lbl_app_name.setStyleSheet("""
            font-size: 20px; 
            font-weight: 900; 
            color: #38bdf8; 
            border: none; 
            margin-bottom: 20px;
        """)
        sidebar_layout.addWidget(lbl_app_name)
        
        # 2. Inisialisasi Tombol dengan Ikon
        self.btn_dashboard = QPushButton("🏠  Dashboard")
        self.btn_data_barang = QPushButton("📦  Data Barang")
        self.btn_riwayat = QPushButton("📜  Riwayat Transaksi")
        self.btn_pengaturan = QPushButton("⚙️  Pengaturan")
        self.btn_logout = QPushButton("🚪  Logout")
        
        # 3. Styling Tombol Navigasi Utama (Modern Hover)
        nav_buttons = [self.btn_dashboard, self.btn_data_barang, self.btn_riwayat, self.btn_pengaturan]
        for btn in nav_buttons:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #94a3b8;
                    padding: 12px 15px;
                    border-radius: 8px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #1e293b;
                    color: #ffffff;
                    border-left: 4px solid #38bdf8; /* Garis biru menyala di kiri saat di-hover */
                    border-top-left-radius: 4px;
                    border-bottom-left-radius: 4px;
                }
            """)
            sidebar_layout.addWidget(btn)
            
        sidebar_layout.addStretch()  # Mendorong tombol logout ke bawah
        
        # 4. Styling Khusus Tombol Logout (Warna Merah)
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #ef4444;
                padding: 12px 15px;
                border-radius: 8px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid transparent;
            }
            QPushButton:hover {
                background-color: #ef4444;
                color: #ffffff;
            }
        """)
        sidebar_layout.addWidget(self.btn_logout)
        
        # ==========================================
        # --- KONTEN KANAN (STACKED WIDGET) ---
        # ==========================================
        self.pages = QStackedWidget()
        self.pages.setStyleSheet("background-color: #111827;") # Latar belakang konten
        
        self.halaman_input = DashboardInput()
        self.halaman_riwayat = RiwayatTransaksi()
        self.halaman_barang = DataBarang()  
        self.halaman_pengaturan = PengaturanWidget()
        
        self.halaman_input.transaksi_disimpan.connect(self.halaman_riwayat.muat_data_ke_tabel)
        
        self.pages.addWidget(self.halaman_input)       
        self.pages.addWidget(self.halaman_riwayat)     
        self.pages.addWidget(self.halaman_barang)      
        self.pages.addWidget(self.halaman_pengaturan)  
        
        self.btn_dashboard.clicked.connect(self.buka_halaman_dashboard)
        self.btn_data_barang.clicked.connect(self.buka_halaman_data_barang)
        self.btn_riwayat.clicked.connect(self.buka_halaman_riwayat)
        self.btn_pengaturan.clicked.connect(lambda: self.pages.setCurrentIndex(3))
        self.btn_logout.clicked.connect(self.proses_logout)
        
        # Masukkan widget ke layout utama
        main_layout.addWidget(self.sidebar_frame)
        main_layout.addWidget(self.pages)
        
        self.buka_halaman_dashboard()

    def buka_halaman_dashboard(self):
        """Menampilkan dashboard dan merefresh otomatis isi pilihan dropdown barang"""
        self.pages.setCurrentIndex(0)
        if hasattr(self.halaman_input, 'muat_pilihan_barang'):
            self.halaman_input.muat_pilihan_barang()
        elif hasattr(self.halaman_input, 'load_combobox_data'):
            self.halaman_input.load_combobox_data()

    def buka_halaman_data_barang(self):
        self.pages.setCurrentIndex(2)
        self.halaman_barang.load_data()  

    def buka_halaman_riwayat(self):
        self.pages.setCurrentIndex(1)
        self.halaman_riwayat.muat_data_ke_tabel()

    def proses_logout(self):
        if apakah_butuh_login():
            konfirmasi = QMessageBox.question(
                self, "Konfirmasi Logout", "Apakah Anda yakin ingin logout?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if konfirmasi == QMessageBox.StandardButton.Yes:
                if self.logout_callback:
                    self.logout_callback()
        else:
            QMessageBox.information(
                self, "Informasi", 
                "Username dan Password login belum diatur di Pengaturan. Fitur login tidak aktif."
            )

def apakah_butuh_login():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "database", "database.db")
    if not os.path.exists(db_path):
        return False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='login_admin'")
        if not cursor.fetchone():
            conn.close()
            return False
        cursor.execute("SELECT username, password FROM login_admin LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row and row[0].strip() and row[1].strip():
            return True
    except Exception as e:
        print(f"Error checking login requirement: {e}")
    return False

class AppController:
    def __init__(self):
        self.login_win = None
        self.main_win = None
        
    def start(self):
        try:
            init_database()
        except Exception as e:
            print(f"Gagal menginisialisasi database: {e}")
            
        if apakah_butuh_login():
            self.show_login()
        else:
            self.show_main()
            
    def show_login(self):
        self.login_win = LoginWindow(self.handle_login_success)
        self.login_win.show()
        if self.main_win:
            self.main_win.close()
            self.main_win = None
            
    def handle_login_success(self):
        self.show_main()
        if self.login_win:
            self.login_win.close()
            self.login_win = None
            
    def show_main(self):
        self.main_win = MainWindow(self.show_login)
        self.main_win.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = AppController()
    controller.start()
    sys.exit(app.exec())