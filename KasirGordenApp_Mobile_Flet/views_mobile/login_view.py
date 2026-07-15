"""
views_mobile/login_view.py
──────────────────────────
Halaman Login — Material Design 3 Premium
Fitur:
  - Desain gradient modern dengan kartu frosted-glass
  - Validasi input real-time (border merah + hint)
  - Async-safe: query DB dijalankan via page.run_thread agar UI tidak freeze
  - SnackBar untuk feedback sukses / gagal
  - Routing ke /dashboard setelah login berhasil
"""

import flet as ft
import threading
from controllers.auth_controller import AuthController


# ─── Palet Warna MD3 ───────────────────────────────────────────────────────────
PRIMARY        = "#1A6EBD"   # Biru utama
PRIMARY_DARK   = "#0D4A8A"   # Biru gelap (hover)
SURFACE        = "#FFFFFF"
ON_SURFACE     = "#1C1B1F"
OUTLINE        = "#79747E"
ERROR_COLOR    = "#B3261E"
SUCCESS_COLOR  = "#2E7D32"
BG_TOP         = "#0D1B2A"   # Gradient atas (biru malam)
BG_BOTTOM      = "#1E3A5F"   # Gradient bawah (biru navy)
CARD_BG        = "#FFFFFFEE" # Putih semi-transparan → efek frosted glass
TEXT_SECONDARY = "#49454F"


def login_view(page: ft.Page) -> ft.View:
    """
    Membuat dan mengembalikan objek ft.View halaman Login.

    Konvensi Flet: Fungsi ini SINKRON (tidak async).
    Operasi database berat dijalankan di thread terpisah via page.run_thread
    sehingga UI tetap responsif.
    """

    # ── State ─────────────────────────────────────────────────────────────────
    is_loading = False  # Guard: mencegah double-submit

    # ── Helper: Tampilkan SnackBar ─────────────────────────────────────────────
    def show_snack(message: str, success: bool = True) -> None:
        page.snack_bar = ft.SnackBar(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        name=ft.Icons.CHECK_CIRCLE if success else ft.Icons.ERROR,
                        color=ft.Colors.WHITE,
                        size=20,
                    ),
                    ft.Text(message, color=ft.Colors.WHITE, size=14),
                ],
                spacing=10,
            ),
            bgcolor=SUCCESS_COLOR if success else ERROR_COLOR,
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    # ── Helper: Set Loading State ──────────────────────────────────────────────
    def set_loading(loading: bool) -> None:
        nonlocal is_loading
        is_loading = loading

        btn_login.disabled = loading
        txt_username.disabled = loading
        txt_password.disabled = loading

        # Ganti teks/icon tombol saat loading
        btn_login.content = (
            ft.Row(
                controls=[
                    ft.ProgressRing(width=18, height=18, stroke_width=2, color=ft.Colors.WHITE),
                    ft.Text("Memverifikasi...", color=ft.Colors.WHITE, size=15, weight=ft.FontWeight.W_600),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            )
            if loading
            else ft.Text("MASUK", color=ft.Colors.WHITE, size=15, weight=ft.FontWeight.W_700, letter_spacing=1.5)
        )
        page.update()

    # ── Helper: Validasi Field ────────────────────────────────────────────────
    def validate_fields() -> bool:
        valid = True

        if not txt_username.value or not txt_username.value.strip():
            txt_username.error_text = "Username tidak boleh kosong"
            txt_username.border_color = ERROR_COLOR
            valid = False
        else:
            txt_username.error_text = None
            txt_username.border_color = None

        if not txt_password.value or not txt_password.value.strip():
            txt_password.error_text = "Password tidak boleh kosong"
            txt_password.border_color = ERROR_COLOR
            valid = False
        else:
            txt_password.error_text = None
            txt_password.border_color = None

        page.update()
        return valid

    # ── Logika Login (dijalankan di thread terpisah) ───────────────────────────
    def _do_login_thread() -> None:
        """
        Fungsi ini berjalan di background thread.
        Melakukan query database tanpa memblokir event-loop Flet.
        """
        username = txt_username.value.strip()
        password = txt_password.value.strip()

        try:
            success, message = AuthController.login(username, password)

            if success:
                # Jalankan update UI dari thread aman
                page.run_task(_navigate_after_login)
            else:
                # Tampilkan error dari thread
                page.run_task(_show_login_error, message)

        except Exception as ex:
            page.run_task(_show_login_error, f"Terjadi kesalahan: {ex}")

    async def _navigate_after_login() -> None:
        """Dipanggil setelah login sukses — navigasi ke dashboard."""
        set_loading(False)
        show_snack("Login Berhasil! Selamat datang 👋", success=True)
        # Jeda singkat agar snackbar terlihat sebelum navigasi
        import asyncio
        await asyncio.sleep(0.8)
        page.go("/dashboard")

    async def _show_login_error(message: str) -> None:
        """Dipanggil saat login gagal — tampilkan error."""
        set_loading(False)
        lbl_error.value = f"⚠ {message}"
        lbl_error.visible = True
        show_snack(message, success=False)

    # ── Event Handler Tombol Login ─────────────────────────────────────────────
    def btn_login_click(e) -> None:
        """Dipicu saat tombol MASUK diklik atau Enter ditekan."""
        nonlocal is_loading
        if is_loading:
            return  # Abaikan jika sedang proses

        # Reset pesan error lama
        lbl_error.visible = False
        lbl_error.value = ""
        page.update()

        # Validasi dulu — jika tidak valid, berhenti
        if not validate_fields():
            return

        # Aktifkan loading state
        set_loading(True)

        # Jalankan autentikasi di thread terpisah agar UI tidak freeze
        threading.Thread(target=_do_login_thread, daemon=True).start()

    # ─────────────────────────────────────────────────────────────────────────
    # ── WIDGET DEFINITIONS ───────────────────────────────────────────────────
    # ─────────────────────────────────────────────────────────────────────────

    # Logo / Ikon Toko
    logo_section = ft.Column(
        controls=[
            ft.Container(
                content=ft.Icon(ft.Icons.STOREFRONT, size=52, color=ft.Colors.WHITE),
                width=90,
                height=90,
                border_radius=25,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[PRIMARY, PRIMARY_DARK],
                ),
                alignment=ft.alignment.center,
                shadow=ft.BoxShadow(
                    blur_radius=20,
                    color=ft.Colors.with_opacity(0.35, PRIMARY),
                    offset=ft.Offset(0, 8),
                ),
            ),
            ft.Text(
                "KASIR GORDEN",
                size=26,
                weight=ft.FontWeight.W_800,
                color=ON_SURFACE,
                letter_spacing=1.5,
            ),
            ft.Text(
                "Sistem Manajemen Toko Gorden",
                size=13,
                color=TEXT_SECONDARY,
                letter_spacing=0.3,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8,
    )

    # Field Username
    txt_username = ft.TextField(
        label="Username",
        hint_text="Masukkan username Anda",
        prefix_icon=ft.Icons.PERSON_OUTLINE_ROUNDED,
        border_radius=14,
        border_color=OUTLINE,
        focused_border_color=PRIMARY,
        focused_border_width=2,
        filled=True,
        fill_color=ft.Colors.with_opacity(0.05, PRIMARY),
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
        text_style=ft.TextStyle(color=ON_SURFACE, size=15),
        cursor_color=PRIMARY,
        autofocus=True,
        on_change=lambda e: _clear_field_error(txt_username),
    )

    # Field Password
    txt_password = ft.TextField(
        label="Password",
        hint_text="Masukkan password Anda",
        prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED,
        password=True,
        can_reveal_password=True,
        border_radius=14,
        border_color=OUTLINE,
        focused_border_color=PRIMARY,
        focused_border_width=2,
        filled=True,
        fill_color=ft.Colors.with_opacity(0.05, PRIMARY),
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
        text_style=ft.TextStyle(color=ON_SURFACE, size=15),
        cursor_color=PRIMARY,
        on_submit=btn_login_click,  # Tekan Enter = submit
        on_change=lambda e: _clear_field_error(txt_password),
    )

    def _clear_field_error(field: ft.TextField) -> None:
        """Bersihkan error saat user mulai mengetik ulang."""
        if field.error_text:
            field.error_text = None
            field.border_color = None
            page.update()

    # Label error global (di bawah form)
    lbl_error = ft.Text(
        value="",
        color=ERROR_COLOR,
        size=13,
        weight=ft.FontWeight.W_500,
        visible=False,
        text_align=ft.TextAlign.CENTER,
    )

    # Tombol MASUK
    btn_login = ft.ElevatedButton(
        content=ft.Text(
            "MASUK",
            color=ft.Colors.WHITE,
            size=15,
            weight=ft.FontWeight.W_700,
            letter_spacing=1.5,
        ),
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: PRIMARY,
                ft.ControlState.HOVERED: PRIMARY_DARK,
                ft.ControlState.DISABLED: ft.Colors.GREY_400,
            },
            shape=ft.RoundedRectangleBorder(radius=14),
            elevation={ft.ControlState.DEFAULT: 4, ft.ControlState.HOVERED: 8},
            shadow_color=ft.Colors.with_opacity(0.3, PRIMARY),
            animation_duration=200,
            padding=ft.padding.symmetric(vertical=18),
        ),
        width=320,
        on_click=btn_login_click,
    )

    # Footer versi aplikasi
    footer = ft.Text(
        "v1.0.0 · KasirGorden Mobile",
        size=11,
        color=ft.Colors.with_opacity(0.5, TEXT_SECONDARY),
        text_align=ft.TextAlign.CENTER,
    )

    # ── Kartu Form (Frosted Glass Effect) ─────────────────────────────────────
    form_card = ft.Container(
        content=ft.Column(
            controls=[
                logo_section,
                ft.Divider(height=24, color=ft.Colors.TRANSPARENT),
                ft.Text(
                    "Masuk ke Akun Anda",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=ON_SURFACE,
                ),
                ft.Text(
                    "Gunakan kredensial yang telah terdaftar",
                    size=12,
                    color=TEXT_SECONDARY,
                ),
                ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                txt_username,
                txt_password,
                lbl_error,
                ft.Divider(height=4, color=ft.Colors.TRANSPARENT),
                btn_login,
                ft.Divider(height=16, color=ft.Colors.TRANSPARENT),
                ft.Divider(thickness=0.5, color=ft.Colors.with_opacity(0.15, OUTLINE)),
                ft.Divider(height=4, color=ft.Colors.TRANSPARENT),
                footer,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        bgcolor=CARD_BG,
        border_radius=24,
        padding=ft.padding.symmetric(horizontal=28, vertical=32),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=40,
            color=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
            offset=ft.Offset(0, 10),
        ),
        # Lebar responsif tapi maks 380
        width=min(page.window_width - 40 if page.window_width else 360, 380),
    )

    # ── Dekorasi Latar Belakang ────────────────────────────────────────────────
    # Lingkaran dekoratif (blobs) agar terlihat dinamis
    blob_top_right = ft.Container(
        width=200,
        height=200,
        border_radius=100,
        bgcolor=ft.Colors.with_opacity(0.12, PRIMARY),
    )

    blob_bottom_left = ft.Container(
        width=150,
        height=150,
        border_radius=75,
        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.CYAN_200),
    )

    background = ft.Container(
        content=ft.Stack(
            controls=[
                # Blob dekoratif pojok kanan atas
                ft.Container(
                    content=blob_top_right,
                    top=-60,
                    right=-60,
                ),
                # Blob dekoratif pojok kiri bawah
                ft.Container(
                    content=blob_bottom_left,
                    bottom=-40,
                    left=-40,
                ),
                # Form kartu di tengah
                ft.Container(
                    content=form_card,
                    alignment=ft.alignment.center,
                    expand=True,
                ),
            ],
            expand=True,
        ),
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[BG_TOP, BG_BOTTOM],
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=40),
    )

    # ── Kembalikan View ────────────────────────────────────────────────────────
    return ft.View(
        route="/login",
        controls=[background],
        padding=0,
        bgcolor=BG_TOP,  # Fallback warna agar tidak pernah putih
        scroll=ft.ScrollMode.AUTO,
    )
