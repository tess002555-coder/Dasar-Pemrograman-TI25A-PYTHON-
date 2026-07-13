from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from db_manager import get_semua_barang # Import fungsi baru

class MainWindow(QWidget):
    def __init__(self, switch_to_login):
        super().__init__()
        self.setWindowTitle("Data Barang - Kasir Gorden")
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Tabel untuk menampilkan barang
        self.tabel_barang = QTableWidget(0, 4)
        self.tabel_barang.setHorizontalHeaderLabels(["ID", "Nama Barang", "Harga", "Stok"])
        self.tabel_barang.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.btn_load = QPushButton("Muat Data Barang")
        self.btn_load.clicked.connect(self.load_data)
        
        layout.addWidget(self.tabel_barang)
        layout.addWidget(self.btn_load)
        
        # Tombol Logout
        btn_logout = QPushButton("LOGOUT")
        btn_logout.clicked.connect(switch_to_login)
        layout.addWidget(btn_logout)

    def load_data(self):
        data = get_semua_barang()
        self.tabel_barang.setRowCount(0)
        for row_idx, row_data in enumerate(data):
            self.tabel_barang.insertRow(row_idx)
            for col_idx, data in enumerate(row_data):
                self.tabel_barang.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))