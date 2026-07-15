from PyQt6.QtWidgets import (QMenu, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox,
                             QTableWidget, QTableWidgetItem, QLabel, QPushButton, QHeaderView, QDialog, QTextEdit)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor
import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DetailRuanganDialog(QDialog):
    """Pop-up dialog khusus untuk menampilkan rincian spesifikasi jendela/ruangan"""
    def __init__(self, id_pesanan, nama_pembeli, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Rincian Detail Ruangan - ID #{id_pesanan} ({nama_pembeli})")
        
        # --- PERBAIKAN 1: Memperbesar Ukuran Default Pop-up Agar Pas Tanpa Potong ---
        self.setMinimumSize(800, 680) 
        self.setStyleSheet("background-color: #0f172a; color: #e2e8f0;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Header Info Utama
        lbl_judul = QLabel(f"📄 NOTA DETAIL RUANGAN")
        lbl_judul.setStyleSheet("font-size: 18px; font-weight: bold; color: #38bdf8; letter-spacing: 1px;")
        
        lbl_sub = QLabel(f"Pelanggan: {nama_pembeli.upper()} (ID Pesanan: #{id_pesanan})")
        lbl_sub.setStyleSheet("font-size: 13px; color: #94a3b8; font-weight: 500;")
        
        layout.addWidget(lbl_judul)
        layout.addWidget(lbl_sub)
        
        # Komponen Utama Teks Detail menggunakan format HTML/Rich Text
        self.txt_detail = QTextEdit()
        self.txt_detail.setReadOnly(True)
        self.txt_detail.setStyleSheet("""
            QTextEdit { 
                background-color: #1e293b; 
                color: #f1f5f9; 
                font-family: 'Segoe UI', Arial, sans-serif; 
                font-size: 13px; 
                border: 1px solid #334155; 
                border-radius: 8px; 
                padding: 15px;
            }
        """)
        layout.addWidget(self.txt_detail)
        
        btn_tutup = QPushButton("Tutup Jendela")
        btn_tutup.setStyleSheet("""
            QPushButton {
                background-color: #334155; 
                color: white; 
                padding: 12px; 
                border-radius: 6px; 
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        btn_tutup.clicked.connect(self.accept)
        layout.addWidget(btn_tutup)
        
        self.muat_detail_dari_db(id_pesanan)
        
    def get_db_path(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "database", "database.db")
        
    def muat_detail_dari_db(self, id_pesanan):
        try:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            
            # 1. Ambil data nominal total bayar dari tabel utama pesanan
            cursor.execute("SELECT total_bayar FROM pesanan WHERE id = ?", (id_pesanan,))
            data_pesanan = cursor.fetchone()
            total_bayar = data_pesanan[0] if data_pesanan else 0
            total_rp = f"Rp {total_bayar:,}".replace(",", ".")
            
            # 2. Ambil detail spesifikasi jendela/ruangan
            cursor.execute("""
                SELECT nama_ruangan, gorden_lebar, gorden_tinggi, gorden_tipe,
                       vitrase_lebar, vitrase_tinggi, vitrase_tipe,
                       aksesoris_batangan, aksesoris_renda, aksesoris_ring, aksesoris_tali_hook
                FROM pesanan_detail WHERE id_pesanan = ?
            """, (id_pesanan,))
            ruangan_list = cursor.fetchall()
            conn.close()
            
            if not ruangan_list:
                self.txt_detail.setHtml("<p style='color: #ef4444; font-weight: bold; font-size:14px;'>⚠️ Tidak ada rincian data ruangan untuk pesanan ini.</p>")
                return
                
            # --- STYLING CSS RESPONSIVE 100% ---
            html_output = """
            <style>
                body { 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    color: #f1f5f9; 
                    background-color: #1e293b; 
                }
                .card-container { 
                    width: 100%; 
                    margin-bottom: 10px;
                }
                .table-gorden { 
                    width: 100%; 
                    table-layout: fixed;
                    border-collapse: collapse; 
                    background-color: #0f172a;
                }
                .table-gorden th, .table-gorden td { 
                    border: 1px solid #334155; 
                    padding: 10px 10px; 
                    font-size: 13px; 
                    text-align: left;
                    vertical-align: middle;
                }
                .table-gorden th { 
                    background-color: #1e293b; 
                    color: #94a3b8; 
                    font-weight: bold; 
                    font-size: 11px;
                    letter-spacing: 0.5px;
                }
                .row-header { 
                    background-color: #162238; 
                    color: #38bdf8; 
                    font-weight: bold; 
                    font-size: 13px;
                }
                .row-total {
                    background-color: #1e293b;
                    font-weight: bold;
                }
                .item-name { font-weight: bold; color: #cbd5e1; }
                .val-ukuran { color: #f59e0b; font-weight: bold; }
                .val-text { color: #f8fafc; }
                .text-center { text-align: center; }
                
                .pembatas-ruangan {
                    border: none;
                    border-top: 2px dashed #475569;
                    margin-top: 30px;
                    margin-bottom: 30px;
                    width: 100%;
                }
            </style>
            """
            
            total_ruangan = len(ruangan_list)
            for idx, r in enumerate(ruangan_list, 1):
                nama_ruang = r[0] if r[0] else f"Kamar / Ruangan {idx}"
                
                g_L, g_T, g_tipe = (r[1] or "-"), (r[2] or "-"), (r[3] or "-")
                v_L, v_T, v_tipe = (r[4] or "-"), (r[5] or "-"), (r[6] or "-")
                batang, renda, ring, hook_tali = (r[7] or "-"), (r[8] or "-"), (r[9] or "-"), (r[10] or "-")
                
                # --- LOGIKA DETEKSI WARNA GORDEN ---
                # Jika input gorden tipe berisi tanda pisah " - " (Contoh: Blackout - Abu Tua)
                # Maka sistem akan memisahkannya ke kolom Jenis & Kolom Warna otomatis
                jenis_gorden = g_tipe
                warna_gorden = "-"
                if " - " in g_tipe:
                    parts = g_tipe.split(" - ", 1)
                    jenis_gorden = parts[0]
                    warna_gorden = parts[1]
                
                ukuran_gorden = f"{g_L}m &times; {g_T}m" if g_L != "-" and g_L != 0.0 else "-"
                ukuran_vitrase = f"{v_L}m &times; {v_T}m" if v_L != "-" and v_L != 0.0 else "-"
                
                html_output += f"""
                <div class="card-container">
                    <table class="table-gorden" border="1" bordercolor="#334155" cellspacing="0" cellpadding="0" width="100%">
                        
                        <tr>
                            <td class="row-header" width="22%">📍 NAMA RUANGAN</td>
                            <td colspan="4" class="row-header" style="color: #ffffff;" width="78%">
                                &nbsp;{nama_ruang.upper()}
                            </td>
                        </tr>
                        
                        <tr>
                            <th width="22%">BARANG</th>
                            <th width="22%">UKURAN (L &times; T)</th>
                            <th width="32%">BAHAN / JENIS</th>
                            <th width="12%" style="text-align: center;">WARNA</th>
                            <th width="12%" style="text-align: center;">QTY</th>
                        </tr>
                        
                        <tr>
                            <td class="item-name">🧵 Gorden</td>
                            <td class="val-ukuran">{ukuran_gorden}</td>
                            <td class="val-text">{jenis_gorden}</td>
                            <td class="val-text text-center" style="color: #38bdf8; font-weight: bold;">{warna_gorden.upper()}</td>
                            <td class="val-text text-center">-</td>
                        </tr>
                        
                        <tr>
                            <td class="item-name">➖ Batang Gorden</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                            <td class="val-text">{batang}</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                        </tr>
                        
                        <tr>
                            <td class="item-name">☁️ Vitrase</td>
                            <td class="val-ukuran">{ukuran_vitrase}</td>
                            <td class="val-text">{v_tipe}</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                        </tr>
                        
                        <tr>
                            <td class="item-name">➖ Batang Vitrase</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                        </tr>
                        
                        <tr>
                            <td class="item-name">🎀 Renda</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                            <td class="val-text">{renda}</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                        </tr>
                        
                        <tr>
                            <td class="item-name">🪝 Hook</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                            <td class="val-text">{hook_tali}</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                        </tr>
                        
                        <tr>
                            <td class="item-name">🎗️ Tali Jendela</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                            <td class="val-text">{hook_tali}</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                        </tr>
                        
                        <tr>
                            <td class="item-name">⭕ Ring</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                            <td class="val-text">{ring}</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                            <td class="text-center" style="color: #64748b;">-</td>
                        </tr>
                        
                        <tr class="row-total">
                            <td colspan="2" style="color: #94a3b8;">💰 TOTAL NOTA BELANJA</td>
                            <td colspan="3" style="color: #10b981; text-align: right; font-size: 14px; font-weight: bold;">
                                {total_rp} &nbsp;
                            </td>
                        </tr>
                    </table>
                </div>
                """
                if idx < total_ruangan:
                    html_output += '<hr class="pembatas-ruangan">'
            
            self.txt_detail.setHtml(html_output)
        except Exception as e:
            self.txt_detail.setHtml(f"<p style='color: #ef4444;'>Gagal memuat detail dari database:<br>{str(e)}</p>")
            
class RiwayatTransaksi(QWidget):
    def __init__(self):
        super().__init__()
        layout_utama = QVBoxLayout(self)
        layout_utama.setContentsMargins(25, 25, 25, 25)
        layout_utama.setSpacing(15)
        
        layout_header_atas = QHBoxLayout()
        layout_judul = QVBoxLayout()
        judul = QLabel("RIWAYAT TRANSAKSI")
        judul.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        sub_judul = QLabel("💡 Klik 2x untuk detail ruangan. Klik kanan baris untuk Mengedit atau Menghapus.")
        sub_judul.setStyleSheet("font-size: 11px; color: #9ca3af;")
        layout_judul.addWidget(judul)
        layout_judul.addWidget(sub_judul)
        layout_header_atas.addLayout(layout_judul)
        layout_header_atas.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.setStyleSheet("background-color: #1f2937; color: #a78bfa; border: 1px solid #4f46e5; padding: 10px 15px; font-weight: bold; border-radius: 6px;")
        self.btn_refresh.clicked.connect(self.muat_data_ke_tabel)
        layout_header_atas.addWidget(self.btn_refresh)
        layout_utama.addLayout(layout_header_atas)
        
        self.tabel = QTableWidget()
        self.tabel.setColumnCount(6)
        self.tabel.setHorizontalHeaderLabels([
            "ID", "Tanggal", "Nama Pembeli", "No. HP / WA", "Alamat Pengiriman", "Total Nota"
        ])
        self.tabel.verticalHeader().setVisible(False)
        
        # --- PERBAIKAN: Menambahkan 'outline: none;' agar tidak ada blok kotak saat sel diklik ---
        self.tabel.setStyleSheet("""
            QTableWidget { 
                background-color: #111827; 
                color: white; 
                gridline-color: #1f2937; 
                border: 1px solid #1f2937;
                outline: none;
            }
            QTableWidget::item {
                outline: none;
                border: none;
            }
            QHeaderView::section { 
                background-color: #1f2937; 
                color: white; 
                font-weight: bold; 
                padding: 8px; 
            }
            QTableWidget::item:selected { 
                background-color: #4f46e5; 
                color: white;
            }
        """)
        
        # Menghilangkan dotted border fokus bawaan Qt
        self.tabel.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        self.tabel.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabel.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabel.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        self.tabel.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabel.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabel.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabel.cellDoubleClicked.connect(self.buka_detail_ruangan)
        self.tabel.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.buka_menu_klik_kanan)
        self.tabel.customContextMenuRequested.connect(self.buka_menu_klik_kanan)
        
        layout_utama.addWidget(self.tabel)
        self.muat_data_ke_tabel()

    def get_db_path(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "database", "database.db")

    def muat_data_transaksi(self):
        self.muat_data_ke_tabel()

    def muat_data_ke_tabel(self):
        self.tabel.setRowCount(0)
        db_path = self.get_db_path()
        
        try:
            conn = sqlite3.connect(db_path)
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
            
            cursor.execute("SELECT id, tanggal, nama_pembeli, no_hp, alamat, total_bayar FROM pesanan ORDER BY id DESC")
            semua_pesanan = cursor.fetchall()
            conn.close()
            
            for row_idx, data in enumerate(semua_pesanan):
                self.tabel.insertRow(row_idx)
                
                id_pesanan = str(data[0])
                tanggal = str(data[1]) if data[1] else ""
                nama = str(data[2]) if data[2] else ""
                hp = str(data[3]) if data[3] else ""
                alamat = str(data[4]) if data[4] else ""
                
                try: total_val = int(data[5]) if data[5] is not None else 0
                except (ValueError, TypeError): total_val = 0
                total_rp = f"Rp {total_val:,}".replace(",", ".")
                
                self.tabel.setItem(row_idx, 0, QTableWidgetItem(id_pesanan))
                self.tabel.setItem(row_idx, 1, QTableWidgetItem(tanggal))
                self.tabel.setItem(row_idx, 2, QTableWidgetItem(nama))
                self.tabel.setItem(row_idx, 3, QTableWidgetItem(hp))
                self.tabel.setItem(row_idx, 4, QTableWidgetItem(alamat))
                
                item_harga = QTableWidgetItem(total_rp)
                item_harga.setForeground(QColor("white"))
                self.tabel.setItem(row_idx, 5, item_harga)
                
                self.tabel.item(row_idx, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabel.item(row_idx, 1).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabel.item(row_idx, 3).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabel.item(row_idx, 5).setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        except Exception as e:
            print(f"Error Muat Tabel Riwayat: {str(e)}")

    def buka_detail_ruangan(self, row, column):
        try:
            id_pesanan = self.tabel.item(row, 0).text()
            nama_pembeli = self.tabel.item(row, 2).text()
            dialog = DetailRuanganDialog(id_pesanan, nama_pembeli, self)
            dialog.exec()
        except Exception as e: 
            print(f"Error Buka Detail: {str(e)}")

    def buka_menu_klik_kanan(self, posisi: QPoint):
        # 1. Cari tahu baris mana yang sedang diklik kanan secara akurat
        item_diklik = self.tabel.itemAt(posisi)
        if not item_diklik: 
            return
            
        index_baris = item_diklik.row()
        self.tabel.selectRow(index_baris)
        
        try:
            id_pesanan = self.tabel.item(index_baris, 0).text()
            nama_pembeli = self.tabel.item(index_baris, 2).text()
        except Exception: 
            return
        
        # 2. Desain komponen menu pop-up
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { 
                background-color: #1f2937; 
                color: white; 
                border: 1px solid #374151;
                border-radius: 4px;
                padding: 4px;
            } 
            QMenu::item {
                padding: 6px 20px;
            }
            QMenu::item:selected { 
                background-color: #4f46e5; 
                border-radius: 4px;
            }
        """)
        
        aksi_lihat = menu.addAction("🔍 Lihat Detail Ruangan")
        aksi_hapus = menu.addAction("🗑️ Hapus Transaksi")
        
        # 3. PERBAIKAN UTAMA: Memaksa menu muncul tepat di posisi kursor mouse saat ini
        from PyQt6.QtGui import QCursor
        aksi_terpilih = menu.exec(QCursor.pos())
        
        # 4. Eksekusi aksi yang dipilih
        if aksi_terpilih == aksi_lihat:
            self.buka_detail_ruangan(index_baris, 0)
        elif aksi_terpilih == aksi_hapus:
            self.proses_hapus_pesanan(id_pesanan, nama_pembeli, index_baris)

    def proses_hapus_pesanan(self, id_pesanan, nama, index_baris):
        tanya = QMessageBox.question(self, "Konfirmasi Hapus", f"Hapus pesanan ID #{id_pesanan} atas nama '{nama}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if tanya == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect(self.get_db_path())
                cursor = conn.cursor()
                cursor.execute("DELETE FROM pesanan_detail WHERE id_pesanan = ?", (id_pesanan,))
                cursor.execute("DELETE FROM pesanan WHERE id = ?", (id_pesanan,))
                conn.commit()
                conn.close()
                self.muat_data_ke_tabel()
                QMessageBox.information(self, "Berhasil", "Pesanan berhasil dihapus.")
            except Exception as e:
                QMessageBox.critical(self, "Gagal", str(e))

BoxRiwayatTransaksi = RiwayatTransaksi
Ui_RiwayatTransaksi = RiwayatTransaksi