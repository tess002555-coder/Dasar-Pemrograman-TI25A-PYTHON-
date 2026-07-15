"""
views_mobile/dashboard_view.py
──────────────────────────────
Halaman Dashboard Utama — KasirGorden Mobile
Menampilkan ringkasan bisnis & menu navigasi utama.
"""

import flet as ft
import sqlite3
import os
import threading
from datetime import datetime

# ── Palet Warna ────────────────────────────────────────────────────────────────
PRIMARY      = "#1A6EBD"
PRIMARY_DK   = "#0D4A8A"
SURFACE      = "#F6F8FB"
CARD_BG      = "#FFFFFF"
ON_SURFACE   = "#1C1B1F"
TEXT_2ND     = "#49454F"
SUCCESS      = "#2E7D32"
WARNING      = "#E65100"
PURPLE       = "#6A1B9A"
TEAL         = "#00695C"
DANGER       = "#B3261E"


def _get_db_path() -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "database", "database.db")


def _fetch_stats() -> dict:
    """Query ringkasan statistik dari database (dijalankan di thread)."""
    stats = {"total_pesanan": 0, "total_omzet": 0, "pesanan_hari_ini": 0}
    try:
        conn = sqlite3.connect(_get_db_path())
        cursor = conn.cursor()

        # Cek & buat tabel pesanan jika belum ada
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
        conn.commit()

        cursor.execute("SELECT COUNT(*), COALESCE(SUM(total_bayar), 0) FROM pesanan")
        row = cursor.fetchone()
        stats["total_pesanan"] = row[0] or 0
        stats["total_omzet"]   = row[1] or 0

        hari_ini = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            "SELECT COUNT(*) FROM pesanan WHERE tanggal LIKE ?",
            (f"{hari_ini}%",)
        )
        stats["pesanan_hari_ini"] = cursor.fetchone()[0] or 0

        conn.close()
    except Exception as ex:
        print(f"[Dashboard] Stats error: {ex}")
    return stats


def dashboard_view(page: ft.Page) -> ft.View:
    """Membangun dan mengembalikan View Dashboard."""

    # ── State refs ────────────────────────────────────────────────────────────
    lbl_total_pesanan  = ft.Text("...", size=28, weight=ft.FontWeight.W_800, color=PRIMARY)
    lbl_omzet          = ft.Text("...", size=22, weight=ft.FontWeight.W_800, color=SUCCESS)
    lbl_hari_ini       = ft.Text("...", size=28, weight=ft.FontWeight.W_800, color=WARNING)

    # ── Load stats di background ──────────────────────────────────────────────
    def _load_stats():
        stats = _fetch_stats()
        omzet_fmt = f"Rp {stats['total_omzet']:,}".replace(",", ".")
        lbl_total_pesanan.value = str(stats["total_pesanan"])
        lbl_omzet.value         = omzet_fmt
        lbl_hari_ini.value      = str(stats["pesanan_hari_ini"])
        try:
            page.update()
        except Exception:
            pass

    threading.Thread(target=_load_stats, daemon=True).start()

    # ── Logout ────────────────────────────────────────────────────────────────
    def do_logout(e):
        page.go("/login")

    # ── AppBar ────────────────────────────────────────────────────────────────
    app_bar = ft.AppBar(
        leading=ft.Container(
            content=ft.Icon(ft.Icons.STOREFRONT, color=ft.Colors.WHITE, size=22),
            margin=ft.margin.only(left=8),
        ),
        title=ft.Text("Kasir Gorden", color=ft.Colors.WHITE, weight=ft.FontWeight.W_700, size=17),
        bgcolor=PRIMARY,
        automatically_imply_leading=False,
        actions=[
            ft.IconButton(
                icon=ft.Icons.LOGOUT_ROUNDED,
                icon_color=ft.Colors.WHITE,
                tooltip="Logout",
                on_click=do_logout,
            )
        ],
    )

    # ── Stat Card ─────────────────────────────────────────────────────────────
    def stat_card(icon, label, value_widget, color, bg_color) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Icon(icon, color=ft.Colors.WHITE, size=22),
                        width=44, height=44,
                        border_radius=12,
                        bgcolor=color,
                        alignment=ft.alignment.center,
                    ),
                    ft.Text(label, size=11, color=TEXT_2ND, weight=ft.FontWeight.W_500),
                    value_widget,
                ],
                spacing=6,
            ),
            bgcolor=CARD_BG,
            border_radius=16,
            padding=16,
            expand=True,
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 3),
            ),
        )

    stats_row = ft.Row(
        controls=[
            stat_card(ft.Icons.RECEIPT_LONG_ROUNDED, "Total Pesanan", lbl_total_pesanan, PRIMARY, CARD_BG),
            stat_card(ft.Icons.TODAY_ROUNDED, "Hari Ini", lbl_hari_ini, WARNING, CARD_BG),
        ],
        spacing=12,
    )

    omzet_card = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(ft.Icons.TRENDING_UP_ROUNDED, color=ft.Colors.WHITE, size=26),
                    width=52, height=52,
                    border_radius=14,
                    bgcolor=SUCCESS,
                    alignment=ft.alignment.center,
                ),
                ft.Column(
                    controls=[
                        ft.Text("Total Omzet", size=12, color=TEXT_2ND),
                        lbl_omzet,
                    ],
                    spacing=2,
                    expand=True,
                ),
            ],
            spacing=14,
        ),
        bgcolor=CARD_BG,
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=16, vertical=14),
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            offset=ft.Offset(0, 3),
        ),
    )

    # ── Menu Grid ────────────────────────────────────────────────────────────
    menus = [
        ("Pesanan Baru",    ft.Icons.ADD_SHOPPING_CART_ROUNDED, PRIMARY,  "/order_new"),
        ("Riwayat",         ft.Icons.HISTORY_ROUNDED,           PURPLE,   "/order_history"),
        ("Data Barang",     ft.Icons.INVENTORY_2_ROUNDED,        WARNING,  "/inventory"),
        ("Pengaturan",      ft.Icons.SETTINGS_ROUNDED,           TEAL,     "/settings"),
    ]

    def menu_btn(label, icon, color, route) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Icon(icon, color=ft.Colors.WHITE, size=24),
                        width=54, height=54,
                        border_radius=16,
                        bgcolor=color,
                        alignment=ft.alignment.center,
                        shadow=ft.BoxShadow(
                            blur_radius=12,
                            color=ft.Colors.with_opacity(0.28, color),
                            offset=ft.Offset(0, 5),
                        ),
                    ),
                    ft.Text(label, size=12, weight=ft.FontWeight.W_600, color=ON_SURFACE,
                            text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=CARD_BG,
            border_radius=18,
            padding=ft.padding.symmetric(horizontal=12, vertical=16),
            expand=True,
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.with_opacity(0.07, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            on_click=lambda e, r=route: page.go(r),
            ink=True,
            ink_color=ft.Colors.with_opacity(0.06, color),
        )

    menu_grid = ft.Column(
        controls=[
            ft.Row(controls=[menu_btn(*menus[0]), menu_btn(*menus[1])], spacing=12),
            ft.Row(controls=[menu_btn(*menus[2]), menu_btn(*menus[3])], spacing=12),
        ],
        spacing=12,
    )

    # ── Body ──────────────────────────────────────────────────────────────────
    salam = datetime.now().hour
    if salam < 11:
        kata_salam = "Selamat Pagi"
    elif salam < 15:
        kata_salam = "Selamat Siang"
    elif salam < 18:
        kata_salam = "Selamat Sore"
    else:
        kata_salam = "Selamat Malam"

    body = ft.ListView(
        controls=[
            # Header salam
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(kata_salam + " 👋", size=13, color=TEXT_2ND),
                        ft.Text("Dashboard Kasir", size=22, weight=ft.FontWeight.W_800, color=ON_SURFACE),
                    ],
                    spacing=2,
                ),
                margin=ft.margin.only(bottom=16),
            ),
            # Stats
            stats_row,
            ft.Container(height=12),
            omzet_card,
            ft.Container(height=20),
            # Menu
            ft.Text("Menu Utama", size=15, weight=ft.FontWeight.W_700, color=ON_SURFACE),
            ft.Container(height=8),
            menu_grid,
            ft.Container(height=24),
        ],
        padding=ft.padding.symmetric(horizontal=16, vertical=16),
        expand=True,
        spacing=0,
    )

    return ft.View(
        route="/dashboard",
        controls=[app_bar, body],
        bgcolor=SURFACE,
        padding=0,
    )
