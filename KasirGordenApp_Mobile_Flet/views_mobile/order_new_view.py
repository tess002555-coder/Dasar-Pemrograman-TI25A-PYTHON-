"""
views_mobile/order_new_view.py
──────────────────────────────
Halaman Input Pesanan Baru — KasirGorden Mobile
Fitur:
  - Data pelanggan (nama, HP, alamat)
  - Multi-ruangan dengan navigasi tab
  - Spesifikasi Gorden & Vitrase (lebar x tinggi x jenis kain)
  - Aksesoris otomatis (batang rel, renda, ring, tali, hook)
  - Kalkulasi harga real-time
  - Simpan ke database dengan validasi
"""

import flet as ft
import sqlite3
import os
import threading
import json

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
AMBER      = "#FF8F00"


def _get_db_path() -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "database", "database.db")


def _load_master_barang() -> tuple[dict, dict]:
    """
    Ambil data master barang dari DB.
    Return: (master_dict, harga_map)
    """
    master = {"Gorden": [], "Vitrase": [], "Aksesoris": []}
    harga  = {}
    try:
        conn   = sqlite3.connect(_get_db_path())
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS barang (id INTEGER PRIMARY KEY AUTOINCREMENT, nama_barang TEXT, kategori TEXT, harga_per_meter INTEGER)")
        cursor.execute("SELECT nama_barang, kategori, harga_per_meter FROM barang")
        rows = cursor.fetchall()
        conn.close()
        for nama, kat, harga_val in rows:
            kat_c = str(kat).strip().capitalize()
            if kat_c not in master:
                kat_c = "Aksesoris"
            if nama not in master[kat_c]:
                master[kat_c].append(nama)
            try:
                harga[nama] = int(str(harga_val).replace(".", "").strip())
            except (ValueError, TypeError):
                harga[nama] = 0
    except Exception as ex:
        print(f"[OrderNew] load barang error: {ex}")
    return master, harga


def _hitung_total(list_ruangan: list, harga_map: dict) -> int:
    """Hitung total harga seluruh ruangan."""
    total = 0
    for r in list_ruangan:
        def safe_float(val):
            try:
                return float(str(val).replace(",", ".")) if val else 0.0
            except ValueError:
                return 0.0

        g_l = safe_float(r.get("g_l"))
        g_t = safe_float(r.get("g_t"))
        v_l = safe_float(r.get("v_l"))
        v_t = safe_float(r.get("v_t"))

        NONE_VAL = "-- Pilih Barang --"

        if r.get("g_tipe") and r["g_tipe"] != NONE_VAL:
            total += int(g_l * g_t * harga_map.get(r["g_tipe"], 0))

        if r.get("v_tipe") and r["v_tipe"] != NONE_VAL and v_l > 0 and v_t > 0:
            total += int(v_l * v_t * harga_map.get(r["v_tipe"], 0))

        if r.get("a_batang") and r["a_batang"] != NONE_VAL and g_l > 0:
            total += int((g_l + 0.2) * harga_map.get(r["a_batang"], 0))

        if r.get("a_batang_v") and r["a_batang_v"] != NONE_VAL and v_l > 0:
            total += int((v_l + 0.2) * harga_map.get(r["a_batang_v"], 0))

        if r.get("a_renda") and r["a_renda"] != NONE_VAL:
            total += int(g_l * harga_map.get(r["a_renda"], 0))

        if r.get("a_ring") and r["a_ring"] != NONE_VAL:
            total += int(g_l * 8 * harga_map.get(r["a_ring"], 0))

        if r.get("a_tali") and r["a_tali"] != NONE_VAL:
            total += int(2 * harga_map.get(r["a_tali"], 0))

        if r.get("a_hook") and r["a_hook"] != NONE_VAL:
            total += int(2 * harga_map.get(r["a_hook"], 0))

    return total


def order_new_view(page: ft.Page) -> ft.View:
    """Membuat dan mengembalikan View Input Pesanan Baru."""

    # ── State ─────────────────────────────────────────────────────────────────
    NONE_VAL = "-- Pilih Barang --"

    list_ruangan: list[dict] = []
    harga_map: dict          = {}
    master_barang: dict      = {"Gorden": [], "Vitrase": [], "Aksesoris": []}
    idx_aktif: list[int]     = [0]   # mutable reference

    def new_room_data(n: int) -> dict:
        return {
            "nama_ruang": f"Ruangan {n}",
            "g_l": "", "g_t": "", "g_tipe": NONE_VAL,
            "v_l": "", "v_t": "", "v_tipe": NONE_VAL,
            "a_batang": NONE_VAL, "a_batang_v": NONE_VAL,
            "a_renda": NONE_VAL, "a_ring": NONE_VAL,
            "a_tali": NONE_VAL,  "a_hook": NONE_VAL,
        }

    list_ruangan.append(new_room_data(1))

    # ── Widgets Data Pelanggan ────────────────────────────────────────────────
    txt_nama    = ft.TextField(label="Nama Pembeli *", hint_text="Nama lengkap pelanggan",
                               prefix_icon=ft.Icons.PERSON_OUTLINE, border_radius=12,
                               filled=True, fill_color=ft.Colors.with_opacity(0.04, PRIMARY))
    txt_hp      = ft.TextField(label="No. HP / WA *", hint_text="08xxxxxxxxxx",
                               prefix_icon=ft.Icons.PHONE_OUTLINED, border_radius=12,
                               filled=True, fill_color=ft.Colors.with_opacity(0.04, PRIMARY),
                               keyboard_type=ft.KeyboardType.PHONE)
    txt_alamat  = ft.TextField(label="Alamat Pengiriman", hint_text="Alamat lengkap pemasangan",
                               prefix_icon=ft.Icons.LOCATION_ON_OUTLINED, border_radius=12,
                               filled=True, fill_color=ft.Colors.with_opacity(0.04, PRIMARY),
                               multiline=True, min_lines=1, max_lines=3)

    # ── Widgets Spesifikasi Ruangan ───────────────────────────────────────────
    txt_nama_ruang = ft.TextField(label="Nama Ruangan", hint_text="Contoh: Kamar Utama",
                                  border_radius=12, filled=True,
                                  fill_color=ft.Colors.with_opacity(0.04, PRIMARY))

    # Gorden
    txt_g_l  = ft.TextField(label="Lebar Gorden (m)", keyboard_type=ft.KeyboardType.NUMBER,
                             border_radius=12, filled=True, expand=True,
                             fill_color=ft.Colors.with_opacity(0.04, PRIMARY))
    txt_g_t  = ft.TextField(label="Tinggi Gorden (m)", keyboard_type=ft.KeyboardType.NUMBER,
                             border_radius=12, filled=True, expand=True,
                             fill_color=ft.Colors.with_opacity(0.04, PRIMARY))

    # Vitrase
    txt_v_l  = ft.TextField(label="Lebar Vitrase (m)", keyboard_type=ft.KeyboardType.NUMBER,
                             border_radius=12, filled=True, expand=True,
                             fill_color=ft.Colors.with_opacity(0.04, PRIMARY))
    txt_v_t  = ft.TextField(label="Tinggi Vitrase (m)", keyboard_type=ft.KeyboardType.NUMBER,
                             border_radius=12, filled=True, expand=True,
                             fill_color=ft.Colors.with_opacity(0.04, PRIMARY))

    # Dropdown helpers
    def make_dd(label: str, options: list[str]) -> ft.Dropdown:
        return ft.Dropdown(
            label=label,
            options=[ft.dropdown.Option(NONE_VAL)] + [ft.dropdown.Option(o) for o in options],
            value=NONE_VAL,
            border_radius=12,
            filled=True,
            fill_color=ft.Colors.with_opacity(0.04, PRIMARY),
            text_size=14,
        )

    dd_g_tipe     = make_dd("Jenis Kain Gorden",  master_barang["Gorden"])
    dd_v_tipe     = make_dd("Jenis Kain Vitrase",  master_barang["Vitrase"])
    dd_a_batang   = make_dd("Rel/Batang Gorden",   master_barang["Aksesoris"])
    dd_a_batang_v = make_dd("Rel/Batang Vitrase",  master_barang["Aksesoris"])
    dd_a_renda    = make_dd("Renda/Poni Gorden",   master_barang["Aksesoris"])
    dd_a_ring     = make_dd("Ring Gorden",         master_barang["Aksesoris"])
    dd_a_tali     = make_dd("Tali Gorden",         master_barang["Aksesoris"])
    dd_a_hook     = make_dd("Hook/Kaitan",         master_barang["Aksesoris"])

    # Label total harga
    lbl_total = ft.Text("Rp 0", size=20, weight=ft.FontWeight.W_800, color=SUCCESS)

    # Navigasi ruangan (chip-like tabs)
    row_tabs = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8)

    def rebuild_tabs():
        row_tabs.controls.clear()
        for i, r in enumerate(list_ruangan):
            active = (i == idx_aktif[0])
            chip = ft.Container(
                content=ft.Text(
                    r["nama_ruang"],
                    size=12,
                    color=ft.Colors.WHITE if active else PRIMARY,
                    weight=ft.FontWeight.W_600,
                ),
                bgcolor=PRIMARY if active else ft.Colors.with_opacity(0.1, PRIMARY),
                border=ft.border.all(1, PRIMARY),
                border_radius=20,
                padding=ft.padding.symmetric(horizontal=14, vertical=7),
                on_click=lambda e, idx=i: switch_room(idx),
                ink=True,
            )
            row_tabs.controls.append(chip)
        # Tombol + tambah ruangan
        row_tabs.controls.append(
            ft.IconButton(
                icon=ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                icon_color=PRIMARY,
                tooltip="Tambah Ruangan",
                on_click=lambda e: tambah_ruangan(),
            )
        )

    def save_current_to_memory():
        idx = idx_aktif[0]
        if idx >= len(list_ruangan):
            return
        r = list_ruangan[idx]
        r["nama_ruang"]  = txt_nama_ruang.value or f"Ruangan {idx + 1}"
        r["g_l"]         = txt_g_l.value or ""
        r["g_t"]         = txt_g_t.value or ""
        r["g_tipe"]      = dd_g_tipe.value or NONE_VAL
        r["v_l"]         = txt_v_l.value or ""
        r["v_t"]         = txt_v_t.value or ""
        r["v_tipe"]      = dd_v_tipe.value or NONE_VAL
        r["a_batang"]    = dd_a_batang.value or NONE_VAL
        r["a_batang_v"]  = dd_a_batang_v.value or NONE_VAL
        r["a_renda"]     = dd_a_renda.value or NONE_VAL
        r["a_ring"]      = dd_a_ring.value or NONE_VAL
        r["a_tali"]      = dd_a_tali.value or NONE_VAL
        r["a_hook"]      = dd_a_hook.value or NONE_VAL

    def load_room_to_form(idx: int):
        r = list_ruangan[idx]
        txt_nama_ruang.value  = r["nama_ruang"]
        txt_g_l.value         = r["g_l"]
        txt_g_t.value         = r["g_t"]
        dd_g_tipe.value       = r["g_tipe"]
        txt_v_l.value         = r["v_l"]
        txt_v_t.value         = r["v_t"]
        dd_v_tipe.value       = r["v_tipe"]
        dd_a_batang.value     = r["a_batang"]
        dd_a_batang_v.value   = r["a_batang_v"]
        dd_a_renda.value      = r["a_renda"]
        dd_a_ring.value       = r["a_ring"]
        dd_a_tali.value       = r["a_tali"]
        dd_a_hook.value       = r["a_hook"]
        update_total()

    def update_total(e=None):
        save_current_to_memory()
        total = _hitung_total(list_ruangan, harga_map)
        lbl_total.value = f"Rp {total:,}".replace(",", ".")
        try:
            page.update()
        except Exception:
            pass

    def switch_room(idx: int):
        save_current_to_memory()
        idx_aktif[0] = idx
        load_room_to_form(idx)
        rebuild_tabs()
        page.update()

    def tambah_ruangan():
        save_current_to_memory()
        n = len(list_ruangan) + 1
        list_ruangan.append(new_room_data(n))
        idx_aktif[0] = n - 1
        load_room_to_form(idx_aktif[0])
        rebuild_tabs()
        page.update()

    def hapus_ruangan(e=None):
        if len(list_ruangan) <= 1:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Minimal harus ada 1 ruangan.", color=ft.Colors.WHITE),
                bgcolor=WARNING,
            )
            page.snack_bar.open = True
            page.update()
            return
        list_ruangan.pop(idx_aktif[0])
        idx_aktif[0] = max(0, idx_aktif[0] - 1)
        load_room_to_form(idx_aktif[0])
        rebuild_tabs()
        update_total()

    # ── Event listeners untuk update total real-time ──────────────────────────
    for wdg in [txt_g_l, txt_g_t, txt_v_l, txt_v_t]:
        wdg.on_change = update_total
    for dd in [dd_g_tipe, dd_v_tipe, dd_a_batang, dd_a_batang_v,
               dd_a_renda, dd_a_ring, dd_a_tali, dd_a_hook]:
        dd.on_change = update_total

    def on_nama_ruang_change(e):
        list_ruangan[idx_aktif[0]]["nama_ruang"] = txt_nama_ruang.value or f"Ruangan {idx_aktif[0]+1}"
        rebuild_tabs()
        page.update()

    txt_nama_ruang.on_change = on_nama_ruang_change

    # ── Simpan Transaksi ──────────────────────────────────────────────────────
    btn_simpan = ft.ElevatedButton(
        content=ft.Text("SIMPAN PESANAN", color=ft.Colors.WHITE, size=14,
                        weight=ft.FontWeight.W_700, letter_spacing=1),
        style=ft.ButtonStyle(
            bgcolor={ft.ControlState.DEFAULT: SUCCESS, ft.ControlState.HOVERED: "#1B5E20",
                     ft.ControlState.DISABLED: ft.Colors.GREY_400},
            shape=ft.RoundedRectangleBorder(radius=14),
            elevation={ft.ControlState.DEFAULT: 4},
            padding=ft.padding.symmetric(vertical=16),
        ),
        expand=True,
    )

    def _do_save():
        nama_pembeli = txt_nama.value.strip() if txt_nama.value else ""
        if not nama_pembeli:
            page.run_task(_show_error_snack, "Nama pembeli wajib diisi!")
            return

        save_current_to_memory()
        total_bayar = _hitung_total(list_ruangan, harga_map)

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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pesanan_detail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_pesanan INTEGER, nama_ruangan TEXT,
                    gorden_lebar REAL, gorden_tinggi REAL, gorden_tipe TEXT,
                    vitrase_lebar REAL, vitrase_tinggi REAL, vitrase_tipe TEXT,
                    aksesoris_batangan TEXT, aksesoris_renda TEXT,
                    aksesoris_ring TEXT, aksesoris_tali_hook TEXT
                )
            """)
            cursor.execute(
                "INSERT INTO pesanan (nama_pembeli, no_hp, alamat, total_bayar) VALUES (?, ?, ?, ?)",
                (nama_pembeli, txt_hp.value or "", txt_alamat.value or "", total_bayar)
            )
            id_pesanan = cursor.lastrowid

            def sf(v):
                try:
                    return float(str(v).replace(",", ".")) if v else 0.0
                except ValueError:
                    return 0.0

            for r in list_ruangan:
                batang_str   = f"Gorden: {r['a_batang']} | Vitrase: {r['a_batang_v']}"
                tali_str     = f"Tali: {r['a_tali']} | Hook: {r['a_hook']}"
                cursor.execute("""
                    INSERT INTO pesanan_detail (
                        id_pesanan, nama_ruangan,
                        gorden_lebar, gorden_tinggi, gorden_tipe,
                        vitrase_lebar, vitrase_tinggi, vitrase_tipe,
                        aksesoris_batangan, aksesoris_renda, aksesoris_ring, aksesoris_tali_hook
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id_pesanan, r["nama_ruang"],
                    sf(r["g_l"]), sf(r["g_t"]), r["g_tipe"],
                    sf(r["v_l"]), sf(r["v_t"]), r["v_tipe"],
                    batang_str, r["a_renda"], r["a_ring"], tali_str
                ))

            conn.commit()
            conn.close()
            page.run_task(_on_save_success, nama_pembeli)

        except Exception as ex:
            page.run_task(_show_error_snack, f"Gagal simpan: {ex}")

    async def _on_save_success(nama: str):
        btn_simpan.disabled = False
        # Reset form
        txt_nama.value   = ""
        txt_hp.value     = ""
        txt_alamat.value = ""
        list_ruangan.clear()
        list_ruangan.append(new_room_data(1))
        idx_aktif[0] = 0
        _refresh_dropdowns()
        load_room_to_form(0)
        rebuild_tabs()
        lbl_total.value = "Rp 0"
        page.snack_bar = ft.SnackBar(
            content=ft.Row(controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
                ft.Text(f"Pesanan '{nama}' berhasil disimpan!", color=ft.Colors.WHITE),
            ], spacing=10),
            bgcolor=SUCCESS,
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    async def _show_error_snack(msg: str):
        btn_simpan.disabled = False
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color=ft.Colors.WHITE),
            bgcolor=ERROR_C,
            duration=3500,
        )
        page.snack_bar.open = True
        page.update()

    def on_simpan_click(e):
        btn_simpan.disabled = True
        page.update()
        threading.Thread(target=_do_save, daemon=True).start()

    btn_simpan.on_click = on_simpan_click

    # ── Load master barang di background ──────────────────────────────────────
    def _refresh_dropdowns():
        opts_g = [ft.dropdown.Option(NONE_VAL)] + [ft.dropdown.Option(o) for o in master_barang["Gorden"]]
        opts_v = [ft.dropdown.Option(NONE_VAL)] + [ft.dropdown.Option(o) for o in master_barang["Vitrase"]]
        opts_a = [ft.dropdown.Option(NONE_VAL)] + [ft.dropdown.Option(o) for o in master_barang["Aksesoris"]]
        dd_g_tipe.options     = opts_g
        dd_v_tipe.options     = opts_v
        dd_a_batang.options   = opts_a
        dd_a_batang_v.options = opts_a
        dd_a_renda.options    = opts_a
        dd_a_ring.options     = opts_a
        dd_a_tali.options     = opts_a
        dd_a_hook.options     = opts_a

    def _bg_load_barang():
        nonlocal harga_map
        mb, hm = _load_master_barang()
        master_barang["Gorden"]    = mb["Gorden"]
        master_barang["Vitrase"]   = mb["Vitrase"]
        master_barang["Aksesoris"] = mb["Aksesoris"]
        harga_map = hm
        _refresh_dropdowns()
        try:
            page.update()
        except Exception:
            pass

    threading.Thread(target=_bg_load_barang, daemon=True).start()

    # ── Build Tabs awal ───────────────────────────────────────────────────────
    rebuild_tabs()
    load_room_to_form(0)

    # ── Section Builder ───────────────────────────────────────────────────────
    def section_card(title: str, icon: str, color: str, content: list) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.Icon(icon, color=color, size=18),
                        ft.Text(title, size=14, weight=ft.FontWeight.W_700, color=ON_SURFACE),
                    ], spacing=8),
                    ft.Divider(height=1, color=ft.Colors.with_opacity(0.15, OUTLINE)),
                    *content,
                ],
                spacing=12,
            ),
            bgcolor=CARD_BG,
            border_radius=16,
            padding=16,
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.with_opacity(0.07, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

    # ── AppBar ────────────────────────────────────────────────────────────────
    app_bar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            icon_color=ft.Colors.WHITE,
            on_click=lambda e: page.go("/dashboard"),
        ),
        title=ft.Text("Pesanan Baru", color=ft.Colors.WHITE, weight=ft.FontWeight.W_700, size=17),
        bgcolor=PRIMARY,
        automatically_imply_leading=False,
    )

    # ── Layout ────────────────────────────────────────────────────────────────
    body = ft.ListView(
        controls=[
            # 1. Data Pelanggan
            section_card("Data Pelanggan", ft.Icons.PERSON_ROUNDED, PRIMARY, [
                txt_nama, txt_hp, txt_alamat,
            ]),
            ft.Container(height=12),

            # 2. Navigasi Ruangan
            ft.Container(
                content=ft.Column(controls=[
                    ft.Row(controls=[
                        ft.Text("Ruangan", size=14, weight=ft.FontWeight.W_700, color=ON_SURFACE, expand=True),
                        ft.TextButton(
                            content=ft.Row(controls=[
                                ft.Icon(ft.Icons.DELETE_OUTLINE_ROUNDED, size=16, color=ERROR_C),
                                ft.Text("Hapus", size=12, color=ERROR_C),
                            ], spacing=4),
                            on_click=hapus_ruangan,
                        ),
                    ]),
                    row_tabs,
                ], spacing=8),
                bgcolor=CARD_BG,
                border_radius=16,
                padding=16,
                shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.07, ft.Colors.BLACK), offset=ft.Offset(0, 2)),
            ),
            ft.Container(height=12),

            # 3. Nama Ruangan
            section_card("Identitas Ruangan", ft.Icons.DOOR_FRONT_DOOR_ROUNDED, AMBER, [
                txt_nama_ruang,
            ]),
            ft.Container(height=12),

            # 4. Spesifikasi Gorden
            section_card("Gorden", ft.Icons.BLINDS_ROUNDED, PRIMARY, [
                ft.Row(controls=[txt_g_l, txt_g_t], spacing=10),
                dd_g_tipe,
                dd_a_batang,
            ]),
            ft.Container(height=12),

            # 5. Spesifikasi Vitrase
            section_card("Vitrase", ft.Icons.CURTAINS_ROUNDED, "#AB47BC", [
                ft.Row(controls=[txt_v_l, txt_v_t], spacing=10),
                dd_v_tipe,
                dd_a_batang_v,
            ]),
            ft.Container(height=12),

            # 6. Aksesoris
            section_card("Aksesoris", ft.Icons.HARDWARE_ROUNDED, WARNING, [
                dd_a_renda,
                dd_a_ring,
                dd_a_tali,
                dd_a_hook,
            ]),
            ft.Container(height=16),

            # 7. Total & Simpan
            ft.Container(
                content=ft.Column(controls=[
                    ft.Row(controls=[
                        ft.Text("Total Harga:", size=13, color=TEXT_2ND, expand=True),
                        lbl_total,
                    ]),
                    ft.Container(height=8),
                    ft.Row(controls=[btn_simpan]),
                ], spacing=4),
                bgcolor=CARD_BG,
                border_radius=16,
                padding=16,
                shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK), offset=ft.Offset(0, 4)),
            ),
            ft.Container(height=24),
        ],
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        spacing=0,
        expand=True,
    )

    return ft.View(
        route="/order_new",
        controls=[app_bar, body],
        bgcolor=SURFACE,
        padding=0,
        scroll=ft.ScrollMode.AUTO,
    )
