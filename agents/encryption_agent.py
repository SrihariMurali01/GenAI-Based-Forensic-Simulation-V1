from cryptography.fernet import Fernet
import os

class EncryptionAgent:
    def __init__(self, key_path="config/encryption.key"):
        """
        Initializes the Encryption Agent.
        """
        self.key = None
        self.key_path = key_path

        # Load or generate encryption key
        if os.path.exists(self.key_path):
            self.load_key()
        else:
            self.generate_key()

    def generate_key(self):
        """
        Generates a new encryption key and saves it to a file.
        """
        self.key = Fernet.generate_key()
        with open(self.key_path, "wb") as key_file:
            key_file.write(self.key)

    def load_key(self):
        """
        Loads the encryption key from a file.
        """
        with open(self.key_path, "rb") as key_file:
            self.key = key_file.read()

    def encrypt_file(self, file_path, output_dir="data/evidence/encrypted/"):
        """
        Encrypts a user-provided image file and saves the encrypted version.
        :param file_path: Path to the image file to be encrypted.
        :param output_dir: Directory to save the encrypted file.
        """
        os.makedirs(output_dir, exist_ok=True)
        encrypted_file_path = os.path.join(output_dir, os.path.basename(file_path) + ".enc")

        with open(file_path, "rb") as file:
            data = file.read()

        fernet = Fernet(self.key)
        encrypted_data = fernet.encrypt(data)

        with open(encrypted_file_path, "wb") as encrypted_file:
            encrypted_file.write(encrypted_data)
        
        return encrypted_file_path

    def decrypt_file(self, encrypted_file_path, output_dir="data/evidence/decrypted/"):
        """
        Decrypts an encrypted image file and saves the decrypted version.
        :param encrypted_file_path: Path to the encrypted file.
        :param output_dir: Directory to save the decrypted file.
        """
        os.makedirs(output_dir, exist_ok=True)
        decrypted_file_path = os.path.join(output_dir, os.path.basename(encrypted_file_path).replace(".enc", ""))

        with open(encrypted_file_path, "rb") as encrypted_file:
            encrypted_data = encrypted_file.read()

        fernet = Fernet(self.key)
        decrypted_data = fernet.decrypt(encrypted_data)

        with open(decrypted_file_path, "wb") as decrypted_file:
            decrypted_file.write(decrypted_data)

        return decrypted_file_path
