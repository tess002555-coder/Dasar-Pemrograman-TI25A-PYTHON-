"""
views_mobile/inventory_view.py
──────────────────────────────
Halaman Data Barang / Inventori — KasirGorden Mobile
Fitur:
  - Daftar master barang (Gorden, Vitrase, Aksesoris) dari DB
  - Tambah barang baru via BottomSheet form
  - Edit & hapus barang via tap
  - Filter per kategori (chip tabs)
  - Validasi input + SnackBar feedback
"""

import flet as ft
import sqlite3
import os
import threading

# ── Konstanta Warna ────────────────────────────────────────────────────────────
PRIMARY    = "#1A6EBD"
PRIMARY_DK = "#0D4A8A"
SURFACE    = "#F6F8FB"
CARD_BG    = "#FFFFFF"
ON_SURFACE = "#1C1B1F"
TEXT_2ND   = "#49454F"
SUCCESS    = "#2E7D32"
WARNING    = "#E65100"
ERROR_C    = "#B3261E"
OUTLINE    = "#79747E"
PURPLE     = "#6A1B9A"
TEAL       = "#00695C"

KATEGORI   = ["Semua", "Gorden", "Vitrase", "Aksesoris"]
KAT_COLOR  = {
    "Gorden":    PRIMARY,
    "Vitrase":   PURPLE,
    "Aksesoris": WARNING,
    "Semua":     TEAL,
}


def _get_db_path() -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "database", "database.db")


def _ensure_table():
    conn   = sqlite3.connect(_get_db_path())
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS barang (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_barang TEXT NOT NULL,
            kategori    TEXT NOT NULL,
            harga_per_meter INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def _fetch_barang(kategori: str = "Semua") -> list[tuple]:
    try:
        _ensure_table()
        conn   = sqlite3.connect(_get_db_path())
        cursor = conn.cursor()
        if kategori == "Semua":
            cursor.execute("SELECT id, nama_barang, kategori, harga_per_meter FROM barang ORDER BY kategori, nama_barang")
        else:
            cursor.execute(
                "SELECT id, nama_barang, kategori, harga_per_meter FROM barang WHERE kategori = ? ORDER BY nama_barang",
                (kategori,)
            )
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as ex:
        print(f"[Inventory] fetch error: {ex}")
        return []


def _save_barang(nama: str, kategori: str, harga: int, barang_id: int | None = None) -> bool:
    try:
        _ensure_table()
        conn   = sqlite3.connect(_get_db_path())
        cursor = conn.cursor()
        if barang_id:
            cursor.execute(
                "UPDATE barang SET nama_barang=?, kategori=?, harga_per_meter=? WHERE id=?",
                (nama, kategori, harga, barang_id)
            )
        else:
            cursor.execute(
                "INSERT INTO barang (nama_barang, kategori, harga_per_meter) VALUES (?, ?, ?)",
                (nama, kategori, harga)
            )
        conn.commit()
        conn.close()
        return True
    except Exception as ex:
        print(f"[Inventory] save error: {ex}")
        return False


def _delete_barang(barang_id: int) -> bool:
    try:
        conn   = sqlite3.connect(_get_db_path())
        cursor = conn.cursor()
        cursor.execute("DELETE FROM barang WHERE id = ?", (barang_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as ex:
        print(f"[Inventory] delete error: {ex}")
        return False


def inventory_view(page: ft.Page) -> ft.View:
    """Membuat dan mengembalikan View Data Barang."""

    # ── State ─────────────────────────────────────────────────────────────────
    filter_aktif: list[str] = ["Semua"]
    list_cards = ft.Column(spacing=10)

    # ── Filter Chips ──────────────────────────────────────────────────────────
    row_filter = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)

    def rebuild_filter_chips():
        row_filter.controls.clear()
        for kat in KATEGORI:
            active = (kat == filter_aktif[0])
            color  = KAT_COLOR.get(kat, PRIMARY)
            chip   = ft.Container(
                content=ft.Text(kat, size=12, color=ft.Colors.WHITE if active else color,
                                weight=ft.FontWeight.W_600),
                bgcolor=color if active else ft.Colors.with_opacity(0.1, color),
                border=ft.border.all(1, color),
                border_radius=20,
                padding=ft.padding.symmetric(horizontal=14, vertical=7),
                on_click=lambda e, k=kat: set_filter(k),
                ink=True,
            )
            row_filter.controls.append(chip)

    def set_filter(kat: str):
        filter_aktif[0] = kat
        rebuild_filter_chips()
        load_data()

    # ── Build Barang Card ────────────────────────────────────────────────────
    def build_barang_card(row: tuple) -> ft.Container:
        bid, nama, kat, harga = row
        try:
            harga_val = int(harga)
        except (ValueError, TypeError):
            harga_val = 0
        harga_fmt = f"Rp {harga_val:,}".replace(",", ".")
        kat_color = KAT_COLOR.get(kat, PRIMARY)

        def on_edit(e):
            open_form_sheet(bid, nama, kat, harga_val)

        def on_hapus(e):
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Hapus Barang?", weight=ft.FontWeight.W_700),
                content=ft.Text(f"'{nama}' akan dihapus dari database."),
                actions=[
                    ft.TextButton("Batal", on_click=lambda e: close_dlg()),
                    ft.TextButton("Hapus", style=ft.ButtonStyle(color=ERROR_C),
                                  on_click=lambda e: confirm_hapus()),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

            def close_dlg():
                dlg.open = False
                page.update()

            def confirm_hapus():
                dlg.open = False
                ok = _delete_barang(bid)
                snack_msg = "Barang berhasil dihapus." if ok else "Gagal menghapus."
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(snack_msg, color=ft.Colors.WHITE),
                    bgcolor=SUCCESS if ok else ERROR_C,
                )
                page.snack_bar.open = True
                load_data()

        return ft.Container(
            content=ft.Row(controls=[
                ft.Container(
                    content=ft.Text(kat[0].upper(), size=14, color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.W_800),
                    width=44, height=44,
                    border_radius=12,
                    bgcolor=kat_color,
                    alignment=ft.alignment.center,
                ),
                ft.Column(controls=[
                    ft.Text(nama, size=14, weight=ft.FontWeight.W_600, color=ON_SURFACE),
                    ft.Row(controls=[
                        ft.Container(
                            content=ft.Text(kat, size=10, color=kat_color, weight=ft.FontWeight.W_600),
                            bgcolor=ft.Colors.with_opacity(0.1, kat_color),
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                        ),
                        ft.Text(harga_fmt, size=13, color=SUCCESS, weight=ft.FontWeight.W_700),
                    ], spacing=8),
                ], spacing=4, expand=True),
                ft.Column(controls=[
                    ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_color=PRIMARY,
                                  icon_size=18, tooltip="Edit", on_click=on_edit),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE_ROUNDED, icon_color=ERROR_C,
                                  icon_size=18, tooltip="Hapus", on_click=on_hapus),
                ], spacing=0),
            ], spacing=12),
            bgcolor=CARD_BG,
            border_radius=14,
            padding=ft.padding.symmetric(horizontal=14, vertical=12),
            shadow=ft.BoxShadow(
                blur_radius=6,
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

    # ── Form BottomSheet ──────────────────────────────────────────────────────
    def open_form_sheet(edit_id=None, init_nama="", init_kat="Gorden", init_harga=0):
        is_edit = edit_id is not None

        txt_f_nama  = ft.TextField(
            label="Nama Barang *",
            value=init_nama,
            hint_text="Misal: Kain Blackout Premium",
            border_radius=12,
            filled=True,
            fill_color=ft.Colors.with_opacity(0.04, PRIMARY),
        )
        dd_f_kat = ft.Dropdown(
            label="Kategori *",
            value=init_kat,
            options=[ft.dropdown.Option(k) for k in ["Gorden", "Vitrase", "Aksesoris"]],
            border_radius=12,
            filled=True,
            fill_color=ft.Colors.with_opacity(0.04, PRIMARY),
        )
        txt_f_harga = ft.TextField(
            label="Harga per Meter/Pcs (Rp) *",
            value=str(init_harga) if init_harga else "",
            hint_text="Masukkan angka saja, misal: 50000",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=12,
            filled=True,
            fill_color=ft.Colors.with_opacity(0.04, PRIMARY),
        )
        lbl_err_form = ft.Text("", color=ERROR_C, size=12, visible=False)

        btn_save_form = ft.ElevatedButton(
            content=ft.Text("Simpan Barang" if is_edit else "Tambah Barang",
                            color=ft.Colors.WHITE, weight=ft.FontWeight.W_700),
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: PRIMARY},
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(vertical=14),
            ),
            expand=True,
        )

        bs = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(controls=[
                            ft.Text("Edit Barang" if is_edit else "Tambah Barang Baru",
                                    size=16, weight=ft.FontWeight.W_700, color=ON_SURFACE, expand=True),
                            ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, icon_color=TEXT_2ND,
                                          on_click=lambda e: close_bs()),
                        ]),
                        ft.Divider(height=1, color=ft.Colors.with_opacity(0.15, OUTLINE)),
                        txt_f_nama,
                        dd_f_kat,
                        txt_f_harga,
                        lbl_err_form,
                        ft.Row(controls=[btn_save_form]),
                        ft.Container(height=8),
                    ],
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=16),
            ),
            enable_drag=True,
        )

        def close_bs():
            bs.open = False
            page.update()

        def on_save_form(e):
            nama_v  = txt_f_nama.value.strip() if txt_f_nama.value else ""
            kat_v   = dd_f_kat.value or "Gorden"
            harga_s = txt_f_harga.value.strip() if txt_f_harga.value else ""

            if not nama_v:
                lbl_err_form.value   = "Nama barang wajib diisi."
                lbl_err_form.visible = True
                page.update()
                return
            try:
                harga_v = int(harga_s.replace(".", "").replace(",", ""))
            except ValueError:
                lbl_err_form.value   = "Harga harus berupa angka."
                lbl_err_form.visible = True
                page.update()
                return

            lbl_err_form.visible = False
            ok = _save_barang(nama_v, kat_v, harga_v, edit_id)
            bs.open = False
            page.snack_bar = ft.SnackBar(
                content=ft.Text(
                    ("Barang berhasil diperbarui." if is_edit else "Barang berhasil ditambahkan.")
                    if ok else "Gagal menyimpan barang.",
                    color=ft.Colors.WHITE,
                ),
                bgcolor=SUCCESS if ok else ERROR_C,
            )
            page.snack_bar.open = True
            load_data()

        btn_save_form.on_click = on_save_form

        page.overlay.append(bs)
        bs.open = True
        page.update()

    # ── Load Data ─────────────────────────────────────────────────────────────
    lbl_loading = ft.Text("Memuat data...", size=13, color=TEXT_2ND, text_align=ft.TextAlign.CENTER)
    lbl_empty   = ft.Text("Belum ada data barang. Tekan + untuk menambah.",
                          size=13, color=TEXT_2ND, text_align=ft.TextAlign.CENTER, italic=True)

    def load_data(e=None):
        list_cards.controls.clear()
        list_cards.controls.append(
            ft.Container(content=lbl_loading, alignment=ft.alignment.center, padding=40)
        )
        try:
            page.update()
        except Exception:
            pass

        def _bg():
            rows = _fetch_barang(filter_aktif[0])
            list_cards.controls.clear()
            if rows:
                for row in rows:
                    list_cards.controls.append(build_barang_card(row))
            else:
                list_cards.controls.append(
                    ft.Container(content=lbl_empty, alignment=ft.alignment.center, padding=40)
                )
            try:
                page.update()
            except Exception:
                pass

        threading.Thread(target=_bg, daemon=True).start()

    # ── AppBar ────────────────────────────────────────────────────────────────
    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            icon_color=ft.Colors.WHITE,
            on_click=lambda e: page.go("/dashboard"),
        ),
        title=ft.Text("Data Barang", color=ft.Colors.WHITE, weight=ft.FontWeight.W_700, size=17),
        bgcolor=PRIMARY,
        automatically_imply_leading=False,
        actions=[
            ft.IconButton(
                icon=ft.Icons.ADD_ROUNDED,
                icon_color=ft.Colors.WHITE,
                tooltip="Tambah Barang",
                on_click=lambda e: open_form_sheet(),
            )
        ],
    )

    rebuild_filter_chips()

    body = ft.Column(
        controls=[
            # Filter chips
            ft.Container(
                content=row_filter,
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
            ),
            # Daftar
            ft.Container(
                content=ft.ListView(
                    controls=[list_cards],
                    padding=ft.padding.symmetric(horizontal=16, vertical=4),
                    spacing=0,
                    expand=True,
                ),
                expand=True,
            ),
        ],
        expand=True,
        spacing=0,
    )

    # FAB
    fab = ft.FloatingActionButton(
        icon=ft.Icons.ADD_ROUNDED,
        bgcolor=PRIMARY,
        foreground_color=ft.Colors.WHITE,
        tooltip="Tambah Barang",
        on_click=lambda e: open_form_sheet(),
        elevation=4,
    )

    load_data()

    return ft.View(
        route="/inventory",
        controls=[app_bar, body],
        bgcolor=SURFACE,
        padding=0,
        floating_action_button=fab,
        floating_action_button_location=ft.FloatingActionButtonLocation.END_FLOAT,
    )
