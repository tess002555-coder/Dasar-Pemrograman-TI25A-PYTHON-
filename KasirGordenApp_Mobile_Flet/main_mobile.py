"""
main_mobile.py
──────────────
Pusat Navigasi (Router) — KasirGorden Mobile
Menggunakan View-based Routing Flet agar tidak terjadi White Screen.

Route Map:
  /            → redirect ke /login
  /login       → Halaman Login
  /dashboard   → Dashboard utama
  /order_new   → Input pesanan baru (multi-ruangan)
  /order_history → Riwayat & detail pesanan
  /inventory   → Master data barang (Gorden/Vitrase/Aksesoris)
  /settings    → Pengaturan akun (placeholder)

Cara Menjalankan:
  python main_mobile.py
  flet run main_mobile.py          (HotReload)
  flet run --android main_mobile.py  (Preview Android)
"""

import flet as ft
import os
import sys

# ── Pastikan root project ada di sys.path ──────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ── Import semua Views ────────────────────────────────────────────────────────
from views_mobile.login_view         import login_view
from views_mobile.dashboard_view     import dashboard_view
from views_mobile.order_new_view     import order_new_view
from views_mobile.order_history_view import order_history_view
from views_mobile.inventory_view     import inventory_view

# ── Konstanta ──────────────────────────────────────────────────────────────────
PRIMARY  = "#1A6EBD"
BG_TOP   = "#0D1B2A"
SURFACE  = "#F6F8FB"


# ─────────────────────────────────────────────────────────────────────────────
# INISIALISASI DATABASE
# ─────────────────────────────────────────────────────────────────────────────

def init_app_database() -> None:
    """Inisialisasi database SQLite saat startup aplikasi."""
    try:
        from database.db import init_database
        init_database()
        print("[DB] OK - Database berhasil diinisialisasi.")
    except Exception as e:
        print(f"[DB] ERROR - Gagal inisialisasi database: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# SETTINGS VIEW (Placeholder)
# ─────────────────────────────────────────────────────────────────────────────

def _build_settings_view(page: ft.Page) -> ft.View:
    """View pengaturan sederhana — placeholder untuk fitur berikutnya."""
    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            icon_color=ft.Colors.WHITE,
            on_click=lambda e: page.go("/dashboard"),
        ),
        title=ft.Text("Pengaturan", color=ft.Colors.WHITE, weight=ft.FontWeight.W_700, size=17),
        bgcolor=PRIMARY,
        automatically_imply_leading=False,
    )

    # Info versi
    info_card = ft.Container(
        content=ft.Column(controls=[
            ft.Row(controls=[
                ft.Icon(ft.Icons.STOREFRONT, color=PRIMARY, size=32),
                ft.Column(controls=[
                    ft.Text("Kasir Gorden Mobile", size=16, weight=ft.FontWeight.W_700, color="#1C1B1F"),
                    ft.Text("Versi 1.0.0", size=12, color="#49454F"),
                ], spacing=2),
            ], spacing=14),
        ]),
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        padding=20,
        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK), offset=ft.Offset(0, 2)),
    )

    def setting_row(icon, label, subtitle="", on_tap=None) -> ft.Container:
        return ft.Container(
            content=ft.Row(controls=[
                ft.Container(
                    content=ft.Icon(icon, color=PRIMARY, size=20),
                    width=40, height=40,
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.1, PRIMARY),
                    alignment=ft.alignment.center,
                ),
                ft.Column(controls=[
                    ft.Text(label, size=14, weight=ft.FontWeight.W_600, color="#1C1B1F"),
                    ft.Text(subtitle, size=12, color="#49454F") if subtitle else ft.Container(),
                ], spacing=2, expand=True),
                ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, color="#79747E", size=20),
            ], spacing=12),
            bgcolor=ft.Colors.WHITE,
            border_radius=14,
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
            on_click=on_tap,
            ink=True,
            shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK), offset=ft.Offset(0, 1)),
        )

    body = ft.ListView(
        controls=[
            ft.Container(
                content=ft.Column(controls=[
                    info_card,
                    ft.Container(height=20),
                    ft.Text("Akun", size=13, color="#49454F", weight=ft.FontWeight.W_600),
                    ft.Container(height=6),
                    setting_row(ft.Icons.LOCK_OUTLINE_ROUNDED, "Ubah Password", "Ganti password login"),
                    ft.Container(height=8),
                    setting_row(ft.Icons.PERSON_OUTLINE_ROUNDED, "Profil Admin", "admin"),
                    ft.Container(height=20),
                    ft.Text("Aplikasi", size=13, color="#49454F", weight=ft.FontWeight.W_600),
                    ft.Container(height=6),
                    setting_row(ft.Icons.BACKUP_ROUNDED, "Backup Database", "Ekspor data ke file"),
                    ft.Container(height=8),
                    setting_row(ft.Icons.INFO_OUTLINE_ROUNDED, "Tentang Aplikasi", "KasirGorden v1.0.0"),
                    ft.Container(height=24),
                    ft.ElevatedButton(
                        content=ft.Row(controls=[
                            ft.Icon(ft.Icons.LOGOUT_ROUNDED, color=ft.Colors.WHITE, size=18),
                            ft.Text("Logout", color=ft.Colors.WHITE, weight=ft.FontWeight.W_700),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                        style=ft.ButtonStyle(
                            bgcolor={ft.ControlState.DEFAULT: "#B3261E"},
                            shape=ft.RoundedRectangleBorder(radius=14),
                            padding=ft.padding.symmetric(vertical=14),
                        ),
                        expand=True,
                        on_click=lambda e: page.go("/login"),
                    ),
                ], spacing=0),
                padding=ft.padding.symmetric(horizontal=16, vertical=16),
            )
        ],
        expand=True,
    )

    return ft.View(
        route="/settings",
        controls=[app_bar, body],
        bgcolor=SURFACE,
        padding=0,
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main(page: ft.Page) -> None:
    """
    Fungsi utama Flet. Mobile-First dengan View-based Routing.

    Semua view dibangun ulang saat route berubah (stateless routing).
    Ini memastikan tidak ada white screen karena view selalu diisi.
    """

    # ── Konfigurasi Page ──────────────────────────────────────────────────────
    page.title       = "Kasir Gorden Mobile"
    page.theme_mode  = ft.ThemeMode.LIGHT
    page.theme       = ft.Theme(
        color_scheme_seed=PRIMARY,
        use_material3=True,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )

    # Simulasi layar mobile saat dijalankan di desktop/laptop
    page.window_width      = 390
    page.window_height     = 844
    page.window_resizable  = False
    page.window.center()

    page.padding = 0
    page.bgcolor = BG_TOP   # Fallback — tidak pernah putih

    # ── Route Handler ─────────────────────────────────────────────────────────
    def route_change(e: ft.RouteChangeEvent) -> None:
        """
        Dipanggil setiap page.go(route).
        Stack views selalu dibersihkan dan diisi ulang sesuai route.
        """
        page.views.clear()
        route = page.route

        # Peta route → fungsi pembuat view
        route_map = {
            "/login":         lambda: login_view(page),
            "/":              lambda: login_view(page),
            "":               lambda: login_view(page),
            "/dashboard":     lambda: dashboard_view(page),
            "/order_new":     lambda: order_new_view(page),
            "/order_history": lambda: order_history_view(page),
            "/inventory":     lambda: inventory_view(page),
            "/settings":      lambda: _build_settings_view(page),
        }

        builder = route_map.get(route)
        if builder:
            page.views.append(builder())
        else:
            print(f"[Router] Route tidak dikenal: '{route}' - redirect /login")
            page.views.append(login_view(page))

        page.update()

    def view_pop(e: ft.ViewPopEvent) -> None:
        """Tangani tombol Back — minimal selalu 1 view di stack."""
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

    # ── Registrasi Event ──────────────────────────────────────────────────────
    page.on_route_change = route_change
    page.on_view_pop     = view_pop

    # ── Mulai di /login ───────────────────────────────────────────────────────
    start_route = page.route if (page.route and page.route not in ("/", "")) else "/login"
    page.go(start_route)


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # 1. Inisialisasi DB sebelum UI berjalan
    init_app_database()

    # 2. Jalankan Flet (ft.run = API terbaru Flet >= 0.80)
    ft.run(main)
    # Untuk build Android/iOS:
    # ft.run(main, view=ft.AppView.FLET_APP)
