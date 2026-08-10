# src/core/crypto_vault.py
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class CryptoVault:
    @staticmethod
    def encrypt_level_1(plaintext: str) -> bytes:
        """Level 1: No Quantum Security (Plain Text)"""
        return plaintext.encode('utf-8')

    @staticmethod
    def decrypt_level_1(ciphertext_bytes: bytes) -> str:
        return ciphertext_bytes.decode('utf-8')

    @staticmethod
    def encrypt_level_2(plaintext: str, qkd_key_hex: str) -> tuple[bytes, bytes]:
        """Level 2: Quantum-aided AES-256 (Uses first 32 bytes of QKD key as seed)"""
        raw_qkd = bytes.fromhex(qkd_key_hex)
        aes_key = raw_qkd[:32]  # Extract 256 bits
        iv = os.urandom(16)
        
        # PKCS7 Padding manually for clean execution
        pad_len = 16 - (len(plaintext) % 16)
        padded_data = plaintext.encode('utf-8') + bytes([pad_len] * pad_len)
        
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return ciphertext, iv

    @staticmethod
    def decrypt_level_2(ciphertext: bytes, qkd_key_hex: str, iv: bytes) -> str:
        raw_qkd = bytes.fromhex(qkd_key_hex)
        aes_key = raw_qkd[:32]
        
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        pad_len = padded_data[-1]
        return padded_data[:-pad_len].decode('utf-8')

    @staticmethod
    def encrypt_level_3_otp(plaintext: str, qkd_key_hex: str) -> bytes:
        """Level 3: Absolute Quantum Secure One-Time Pad (Plaintext length <= QKD key length)"""
        p_bytes = plaintext.encode('utf-8')
        k_bytes = bytes.fromhex(qkd_key_hex)
        
        if len(p_bytes) > len(k_bytes):
            raise ValueError("Data payload exceeds maximum 1Kb One-Time Pad size limitation!")
            
        return bytes(p ^ k for p, k in zip(p_bytes, k_bytes))

    @staticmethod
    def decrypt_level_3_otp(ciphertext_bytes: bytes, qkd_key_hex: str) -> str:
        k_bytes = bytes.fromhex(qkd_key_hex)
        decrypted = bytes(c ^ k for c, k in zip(ciphertext_bytes, k_bytes))
        return decrypted.decode('utf-8')

