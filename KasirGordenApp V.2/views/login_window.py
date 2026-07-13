from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFrame,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette


class LoginWindow(QWidget):
    def __init__(self, switch_to_main):
        super().__init__()
        self.switch_to_main = switch_to_main
        self.setWindowTitle("Login - Kasir Gorden")
        # Window sedikit diperbesar dari versi lama (350x420) agar ada ruang
        # napas di sekeliling kartu login -> efek "melayang" (floating card).
        self.setFixedSize(420, 560)

        # Pastikan background-color pada QWidget polos ini benar-benar dicat
        # oleh Qt (bukan cuma diwariskan lewat palette bawaan).
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #0f172a;")  # senada dengan sidebar utama

        # ------------------------------------------------------------
        # Layout terluar: taruh login_box di tengah, dikelilingi stretch
        # kiri-kanan-atas-bawah supaya kartu benar2 terlihat mengambang
        # di atas latar gelap, bukan menempel penuh ke tepi window.
        # ------------------------------------------------------------
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.login_box = QFrame()
        self.login_box.setObjectName("loginBox")
        self.login_box.setFixedWidth(340)

        # Bayangan lembut warna indigo di belakang kartu -> kesan "melayang"
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(55)
        shadow.setXOffset(0)
        shadow.setYOffset(16)
        shadow.setColor(QColor(79, 70, 229, 130))  # indigo, semi-transparan
        self.login_box.setGraphicsEffect(shadow)

        box_layout = QVBoxLayout(self.login_box)
        box_layout.setContentsMargins(34, 38, 34, 32)
        box_layout.setSpacing(16)

        # --- Badge ikon bulat bergradasi indigo -> cyan, identitas brand ---
        icon_badge = QLabel("🧵")
        icon_badge.setFixedSize(60, 60)
        icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_badge.setStyleSheet("""
            QLabel {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4f46e5, stop:1 #38bdf8
                );
                border-radius: 30px;
                font-size: 26px;
            }
        """)

        title = QLabel("KASIR GORDEN")
        title.setStyleSheet("""
            color: #f8fafc;
            font-size: 22px;
            font-weight: 800;
            letter-spacing: 1.5px;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Silakan masuk untuk mengelola transaksi")
        subtitle.setStyleSheet("""
            color: #64748b;
            font-size: 12px;
            font-weight: 500;
            background: transparent;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.user = QLineEdit()
        self.user.setPlaceholderText("Username")
        self.pw = QLineEdit()
        self.pw.setPlaceholderText("Password")
        self.pw.setEchoMode(QLineEdit.EchoMode.Password)

        # Warna placeholder abu-abu redup diatur lewat QPalette, karena
        # properti QSS "::placeholder" tidak didukung resmi oleh QLineEdit
        # di PyQt6 -- ini cara yang benar-benar akan tampil di layar.
        for field in (self.user, self.pw):
            pal = field.palette()
            pal.setColor(QPalette.ColorRole.PlaceholderText, QColor("#64748b"))
            field.setPalette(pal)

        self.btn = QPushButton("LOGIN")
        self.btn.setObjectName("btnLogin")
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.clicked.connect(self.process_login)
        # Kenyamanan tambahan: tekan Enter di kolom password langsung login.
        # Ini hanya menambah pemicu baru, TIDAK mengubah isi/logika process_login.
        self.pw.returnPressed.connect(self.process_login)

        # Satu blok QSS di-scope lewat objectName #loginBox, jadi otomatis
        # berlaku untuk QLineEdit & QPushButton di dalamnya juga (DRY).
        self.login_box.setStyleSheet("""
            QFrame#loginBox {
                background-color: #1e293b;
                border-radius: 22px;
                border: 1px solid #334155;
            }
            QFrame#loginBox QLineEdit {
                background-color: #0f172a;
                color: #f1f5f9;
                border: 1.5px solid #334155;
                border-radius: 10px;
                padding: 13px 14px;
                font-size: 13px;
                selection-background-color: #4f46e5;
            }
            QFrame#loginBox QLineEdit:focus {
                border: 1.5px solid #4f46e5;
                background-color: #17233f;
            }
            QPushButton#btnLogin {
                color: #ffffff;
                font-weight: 700;
                font-size: 14px;
                padding: 13px;
                border-radius: 10px;
                border: none;
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4f46e5, stop:1 #6366f1
                );
            }
            QPushButton#btnLogin:hover {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #818cf8
                );
            }
            QPushButton#btnLogin:pressed {
                background-color: #4338ca;
            }
        """)

        box_layout.addWidget(icon_badge, alignment=Qt.AlignmentFlag.AlignCenter)
        box_layout.addWidget(title)
        box_layout.addWidget(subtitle)
        box_layout.addSpacing(10)
        box_layout.addWidget(self.user)
        box_layout.addWidget(self.pw)
        box_layout.addSpacing(6)
        box_layout.addWidget(self.btn)

        layout.addStretch()
        layout.addWidget(self.login_box, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def get_db_path(self):
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "database", "database.db")

    def process_login(self):
        import sqlite3
        from PyQt6.QtWidgets import QMessageBox
        
        username_input = self.user.text().strip()
        password_input = self.pw.text().strip()
        
        if not username_input or not password_input:
            QMessageBox.warning(self, "Peringatan", "Username dan Password tidak boleh kosong!")
            return
            
        try:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            # Cek apakah tabel login_admin ada
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='login_admin'")
            if not cursor.fetchone():
                db_username, db_password = "admin", "admin"
            else:
                cursor.execute("SELECT username, password FROM login_admin LIMIT 1")
                row = cursor.fetchone()
                if row:
                    db_username, db_password = row
                else:
                    db_username, db_password = "admin", "admin"
            conn.close()
            
            if username_input == db_username and password_input == db_password:
                self.switch_to_main()
            else:
                QMessageBox.warning(self, "Login Gagal", "Username atau Password salah!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memproses login: {str(e)}")