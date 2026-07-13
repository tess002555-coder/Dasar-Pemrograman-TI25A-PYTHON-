class AuthController:
    @staticmethod
    def login(username, password):
        # Saat ini login hardcoded "admin" agar aplikasi bisa jalan dulu
        if username == "admin" and password == "admin":
            return True
        return False