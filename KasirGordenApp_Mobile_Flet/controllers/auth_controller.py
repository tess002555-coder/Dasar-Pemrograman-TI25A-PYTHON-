import sqlite3
import os


class AuthController:
    """
    Controller autentikasi yang terhubung ke database SQLite.
    Mendukung login via tabel login_admin atau fallback ke hardcoded admin.
    """

    @staticmethod
    def _get_db_path() -> str:
        """Mengembalikan path absolut database yang benar."""
        # Dari controllers/ naik ke root project, lalu masuk database/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "database", "database.db")

    @staticmethod
    def _ensure_admin_exists(cursor: sqlite3.Cursor) -> None:
        """
        Menjamin selalu ada akun admin default jika tabel login_admin kosong.
        Password default: 'admin' (plaintext, karena tabel lama belum pakai hash).
        """
        cursor.execute("SELECT COUNT(*) FROM login_admin")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute(
                "INSERT INTO login_admin (username, password) VALUES (?, ?)",
                ("admin", "admin"),
            )

    @staticmethod
    def login(username: str, password: str) -> tuple[bool, str]:
        """
        Melakukan autentikasi user terhadap database.

        Args:
            username: Username yang dimasukkan pengguna.
            password: Password plaintext yang dimasukkan pengguna.

        Returns:
            Tuple (success: bool, message: str).
            - (True,  "Login berhasil!") jika autentikasi sukses.
            - (False, "<pesan error>")   jika gagal atau terjadi exception.
        """
        if not username or not password:
            return False, "Username dan password tidak boleh kosong."

        db_path = AuthController._get_db_path()

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Buat tabel jika belum ada (jaga-jaga DB fresh)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS login_admin (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT    NOT NULL,
                    password TEXT    NOT NULL
                )
            """)
            AuthController._ensure_admin_exists(cursor)
            conn.commit()

            # Cari user berdasarkan username (case-insensitive)
            cursor.execute(
                "SELECT password FROM login_admin WHERE LOWER(username) = LOWER(?)",
                (username,),
            )
            row = cursor.fetchone()

            if row is None:
                return False, "Username tidak ditemukan."

            stored_password = row[0]

            # Cek password — mendukung plaintext (lama) & SHA-256 hash (baru)
            from utils.security import verify_password, hash_password

            password_cocok = (
                stored_password == password                   # plaintext lama
                or verify_password(stored_password, password) # SHA-256 hash baru
            )

            if password_cocok:
                return True, "Login berhasil!"
            else:
                return False, "Password salah. Coba lagi."

        except sqlite3.Error as db_err:
            return False, f"Kesalahan database: {db_err}"
        except Exception as ex:
            return False, f"Terjadi kesalahan tak terduga: {ex}"
        finally:
            try:
                conn.close()
            except Exception:
                pass