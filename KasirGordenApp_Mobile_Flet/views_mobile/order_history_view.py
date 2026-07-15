"""
views_mobile/order_history_view.py
────────────────────────────────────
Halaman Riwayat Pesanan — KasirGorden Mobile
Fitur:
  - Daftar pesanan (terbaru di atas)
  - Tap untuk lihat detail ruangan per pesanan
  - Swipe/tombol untuk hapus pesanan
  - Cari berdasarkan nama pembeli
  - Pull-to-refresh (tombol refresh)
"""

import flet as ft
import sqlite3
import os
import threading

# ── Konstanta Warna ─────────────────────────────────────────────────────────
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


def _get_db_path() -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "database", "database.db")


def _fetch_all_orders(search: str = "") -> list[tuple]:
    """Ambil semua pesanan dari DB, opsional filter nama."""
    try:
        conn   = sqlite3.connect(_get_db_path())
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pesanan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_pembeli TEXT, no_hp TEXT, alamat TEXT,
                total_bayar INTEGER DEFAULT 0,
                tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        if search:
            cursor.execute(
                "SELECT id, tanggal, nama_pembeli, no_hp, alamat, total_bayar FROM pesanan "
                "WHERE LOWER(nama_pembeli) LIKE ? ORDER BY id DESC",
                (f"%{search.lower()}%",)
            )
        else:
            cursor.execute(
                "SELECT id, tanggal, nama_pembeli, no_hp, alamat, total_bayar FROM pesanan ORDER BY id DESC"
            )
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as ex:
        print(f"[History] fetch error: {ex}")
        return []


def _fetch_detail_rooms(id_pesanan: int) -> list[tuple]:
    """Ambil detail ruangan per pesanan."""
    try:
        conn   = sqlite3.connect(_get_db_path())
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nama_ruangan, gorden_lebar, gorden_tinggi, gorden_tipe,
                   vitrase_lebar, vitrase_tinggi, vitrase_tipe,
                   aksesoris_batangan, aksesoris_renda, aksesoris_ring, aksesoris_tali_hook
            FROM pesanan_detail WHERE id_pesanan = ?
        """, (id_pesanan,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def _delete_order(id_pesanan: int) -> bool:
    try:
        conn   = sqlite3.connect(_get_db_path())
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pesanan_detail WHERE id_pesanan = ?", (id_pesanan,))
        cursor.execute("DELETE FROM pesanan WHERE id = ?", (id_pesanan,))
        conn.commit()
        conn.close()
        return True
    except Exception as ex:
        print(f"[History] delete error: {ex}")
        return False


def order_history_view(page: ft.Page) -> ft.View:
    """Membuat dan mengembalikan View Riwayat Pesanan."""

    # ── State ─────────────────────────────────────────────────────────────────
    list_cards    = ft.Column(spacing=10, expand=True)
    lbl_empty     = ft.Text("Belum ada pesanan.", size=14, color=TEXT_2ND, italic=True,
                            text_align=ft.TextAlign.CENTER)
    lbl_loading   = ft.Text("Memuat data...", size=13, color=TEXT_2ND,
                            text_align=ft.TextAlign.CENTER)
    txt_search    = ft.TextField(
        hint_text="Cari nama pembeli...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        border_radius=14,
        filled=True,
        fill_color=ft.Colors.with_opacity(0.06, PRIMARY),
        text_size=14,
        height=48,
    )

    # ── Detail Sheet ──────────────────────────────────────────────────────────
    def show_detail_sheet(id_pesanan: int, nama: str, tanggal: str, total: int):
        rooms = _fetch_detail_rooms(id_pesanan)
        total_fmt = f"Rp {total:,}".replace(",", ".")

        def room_card(r: tuple) -> ft.Container:
            nama_r  = r[0] or "Ruangan"
            g_l, g_t, g_t2 = r[1], r[2], r[3] or "-"
            v_l, v_t, v_t2 = r[4], r[5], r[6] or "-"
            batang   = r[7] or "-"
            renda    = r[8] or "-"
            ring     = r[9] or "-"
            hook_tal = r[10] or "-"

            def row_info(label: str, val: str, val_color=ON_SURFACE) -> ft.Row:
                return ft.Row(controls=[
                    ft.Text(label, size=12, color=TEXT_2ND, width=110),
                    ft.Text(str(val), size=12, color=val_color, weight=ft.FontWeight.W_500, expand=True),
                ])

            ukuran_g = f"{g_l}m x {g_t}m" if g_l else "-"
            ukuran_v = f"{v_l}m x {v_t}m" if v_l else "-"

            return ft.Container(
                content=ft.Column(controls=[
                    ft.Container(
                        content=ft.Text(nama_r.upper(), size=13, weight=ft.FontWeight.W_700,
                                        color=ft.Colors.WHITE),
                        bgcolor=PRIMARY,
                        border_radius=ft.border_radius.only(top_left=12, top_right=12),
                        padding=ft.padding.symmetric(horizontal=14, vertical=10),
                    ),
                    ft.Container(
                        content=ft.Column(controls=[
                            row_info("Gorden:", ukuran_g, PRIMARY),
                            row_info("Jenis Kain:", g_t2),
                            row_info("Batang:", batang),
                            ft.Divider(height=1, color=ft.Colors.with_opacity(0.12, OUTLINE)),
                            row_info("Vitrase:", ukuran_v, PURPLE),
                            row_info("Jenis Vitrase:", v_t2),
                            ft.Divider(height=1, color=ft.Colors.with_opacity(0.12, OUTLINE)),
                            row_info("Renda:", renda),
                            row_info("Ring:", ring),
                            row_info("Hook/Tali:", hook_tal),
                        ], spacing=6),
                        padding=ft.padding.symmetric(horizontal=14, vertical=10),
                    ),
                ], spacing=0),
                border=ft.border.all(1, ft.Colors.with_opacity(0.12, OUTLINE)),
                border_radius=12,
            )

        content_controls = [
            ft.Container(
                content=ft.Column(controls=[
                    ft.Text(nama.upper(), size=16, weight=ft.FontWeight.W_800, color=ON_SURFACE),
                    ft.Text(tanggal, size=12, color=TEXT_2ND),
                    ft.Row(controls=[
                        ft.Text("Total:", size=13, color=TEXT_2ND),
                        ft.Text(total_fmt, size=16, weight=ft.FontWeight.W_700, color=SUCCESS),
                    ], spacing=8),
                ], spacing=4),
                padding=ft.padding.only(bottom=12),
            ),
            ft.Divider(height=1, color=ft.Colors.with_opacity(0.15, OUTLINE)),
            ft.Container(height=8),
            ft.Text(f"Detail Ruangan ({len(rooms)} ruang):", size=13,
                    weight=ft.FontWeight.W_600, color=ON_SURFACE),
            ft.Container(height=8),
        ]

        if rooms:
            for r in rooms:
                content_controls.append(room_card(r))
                content_controls.append(ft.Container(height=8))
        else:
            content_controls.append(
                ft.Text("Tidak ada data ruangan.", size=13, color=TEXT_2ND, italic=True)
            )

        bs = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(controls=[
                            ft.Text("Detail Pesanan", size=16, weight=ft.FontWeight.W_700,
                                    color=ON_SURFACE, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE_ROUNDED,
                                icon_color=TEXT_2ND,
                                on_click=lambda e: close_sheet(),
                            ),
                        ]),
                        ft.Divider(height=1, color=ft.Colors.with_opacity(0.15, OUTLINE)),
                        ft.Column(
                            controls=content_controls,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ],
                    spacing=10,
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=16),
                height=page.window_height * 0.75 if page.window_height else 600,
            ),
            enable_drag=True,
        )

        def close_sheet():
            bs.open = False
            page.update()

        page.overlay.append(bs)
        bs.open = True
        page.update()

    # ── Build Order Card ──────────────────────────────────────────────────────
    def build_order_card(row: tuple) -> ft.Container:
        pid, tanggal, nama, hp, alamat, total_bayar = row
        try:
            total_val = int(total_bayar) if total_bayar is not None else 0
        except (ValueError, TypeError):
            total_val = 0
        total_fmt = f"Rp {total_val:,}".replace(",", ".")
        tgl_str   = str(tanggal)[:16] if tanggal else "-"

        def on_tap(e):
            show_detail_sheet(pid, nama or "-", tgl_str, total_val)

        def on_hapus(e):
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Hapus Pesanan?", weight=ft.FontWeight.W_700),
                content=ft.Text(f"Pesanan atas nama '{nama}' akan dihapus permanen."),
                actions=[
                    ft.TextButton("Batal", on_click=lambda e: close_dlg()),
                    ft.TextButton(
                        "Hapus",
                        style=ft.ButtonStyle(color=ERROR_C),
                        on_click=lambda e: confirm_hapus(),
                    ),
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
                page.update()
                ok = _delete_order(pid)
                if ok:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Pesanan berhasil dihapus.", color=ft.Colors.WHITE),
                        bgcolor=SUCCESS,
                    )
                else:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Gagal menghapus pesanan.", color=ft.Colors.WHITE),
                        bgcolor=ERROR_C,
                    )
                page.snack_bar.open = True
                load_data()

        return ft.Container(
            content=ft.Column(controls=[
                ft.Row(controls=[
                    ft.Container(
                        content=ft.Text(str(pid), size=11, color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.W_700),
                        bgcolor=PRIMARY,
                        border_radius=8,
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    ),
                    ft.Text(tgl_str, size=11, color=TEXT_2ND, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                        icon_color=ERROR_C,
                        icon_size=18,
                        tooltip="Hapus",
                        on_click=on_hapus,
                    ),
                ], spacing=8),
                ft.Text(nama or "-", size=15, weight=ft.FontWeight.W_700, color=ON_SURFACE),
                ft.Row(controls=[
                    ft.Icon(ft.Icons.PHONE_OUTLINED, size=13, color=TEXT_2ND),
                    ft.Text(hp or "-", size=12, color=TEXT_2ND),
                ], spacing=4),
                ft.Row(controls=[
                    ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=13, color=TEXT_2ND),
                    ft.Text(alamat or "-", size=12, color=TEXT_2ND, expand=True),
                ], spacing=4),
                ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, OUTLINE)),
                ft.Row(controls=[
                    ft.Text("Total Nota:", size=12, color=TEXT_2ND, expand=True),
                    ft.Text(total_fmt, size=14, weight=ft.FontWeight.W_700, color=SUCCESS),
                ]),
            ], spacing=6),
            bgcolor=CARD_BG,
            border_radius=16,
            padding=16,
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.with_opacity(0.07, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            on_click=on_tap,
            ink=True,
        )

    # ── Load Data ─────────────────────────────────────────────────────────────
    def load_data(e=None):
        list_cards.controls.clear()
        list_cards.controls.append(lbl_loading)
        try:
            page.update()
        except Exception:
            pass

        def _bg():
            search = txt_search.value.strip() if txt_search.value else ""
            rows   = _fetch_all_orders(search)
            list_cards.controls.clear()
            if rows:
                for row in rows:
                    list_cards.controls.append(build_order_card(row))
            else:
                lbl_empty.value = "Tidak ada pesanan ditemukan." if search else "Belum ada pesanan."
                list_cards.controls.append(
                    ft.Container(content=lbl_empty, alignment=ft.alignment.center, padding=40)
                )
            try:
                page.update()
            except Exception:
                pass

        threading.Thread(target=_bg, daemon=True).start()

    txt_search.on_submit = load_data
    txt_search.on_change = lambda e: load_data() if len(txt_search.value or "") != 1 else None

    # ── AppBar ────────────────────────────────────────────────────────────────
    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            icon_color=ft.Colors.WHITE,
            on_click=lambda e: page.go("/dashboard"),
        ),
        title=ft.Text("Riwayat Pesanan", color=ft.Colors.WHITE,
                      weight=ft.FontWeight.W_700, size=17),
        bgcolor=PRIMARY,
        automatically_imply_leading=False,
        actions=[
            ft.IconButton(
                icon=ft.Icons.REFRESH_ROUNDED,
                icon_color=ft.Colors.WHITE,
                tooltip="Refresh",
                on_click=load_data,
            )
        ],
    )

    body = ft.Column(
        controls=[
            ft.Container(content=txt_search, padding=ft.padding.symmetric(horizontal=16, vertical=10)),
            ft.Container(
                content=ft.ListView(
                    controls=[list_cards],
                    padding=ft.padding.symmetric(horizontal=16),
                    spacing=0,
                    expand=True,
                ),
                expand=True,
            ),
        ],
        expand=True,
        spacing=0,
    )

    # Load data saat view pertama dibuka
    load_data()

    return ft.View(
        route="/order_history",
        controls=[app_bar, body],
        bgcolor=SURFACE,
        padding=0,
    )
