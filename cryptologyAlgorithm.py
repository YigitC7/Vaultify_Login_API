from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from hashlib import sha256
import base64


class UltraEncrypt:

    def __init__(self, password):
        self.key = sha256(password.encode()).digest()

    # BYTE padding
    def _pad(self, data):
        padding = 16 - len(data) % 16
        return data + bytes([padding]) * padding

    # BYTE unpadding
    def _unpad(self, data):
        padding = data[-1]
        return data[:-padding]

    # Şifreleme
    def encrypt(self, text):

        data = text.encode("utf-8")

        data = self._pad(data)

        iv = get_random_bytes(16)

        cipher = AES.new(
            self.key,
            AES.MODE_CBC,
            iv
        )

        encrypted = cipher.encrypt(data)

        final_data = iv + encrypted

        return base64.b64encode(final_data).decode()

    # Çözme
    def decrypt(self, encrypted_text):

        raw = base64.b64decode(encrypted_text)

        iv = raw[:16]

        encrypted = raw[16:]

        cipher = AES.new(
            self.key,
            AES.MODE_CBC,
            iv
        )

        decrypted = cipher.decrypt(encrypted)

        decrypted = self._unpad(decrypted)

        return decrypted.decode("utf-8")

    # Dosya şifreleme
    def encrypt_file(self, input_file, output_file):

        with open(input_file, "rb") as f:
            data = f.read()

        data = self._pad(data)

        iv = get_random_bytes(16)

        cipher = AES.new(
            self.key,
            AES.MODE_CBC,
            iv
        )

        encrypted = cipher.encrypt(data)

        final_data = iv + encrypted

        with open(output_file, "wb") as f:
            f.write(base64.b64encode(final_data))

    # Dosya çözme
    def decrypt_file(self, input_file, output_file):

        with open(input_file, "rb") as f:
            raw = base64.b64decode(f.read())

        iv = raw[:16]

        encrypted = raw[16:]

        cipher = AES.new(
            self.key,
            AES.MODE_CBC,
            iv
        )

        decrypted = cipher.decrypt(encrypted)

        decrypted = self._unpad(decrypted)

        with open(output_file, "wb") as f:
            f.write(decrypted)
