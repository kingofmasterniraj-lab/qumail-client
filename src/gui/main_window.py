# src/gui/main_window.py
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QTextEdit, QLineEdit, QComboBox, QPushButton, QMessageBox)
from src.core.crypto_vault import CryptoVault
from src.core.key_manager_api import KeyManagerClient
from src.core.email_engine import EmailEngine

class QuMailWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuMail - Quantum Secure Email Client")
        self.setGeometry(100, 100, 700, 550)
        self.km_client = KeyManagerClient()
        self.init_ui()
        
    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()
        
        # Configuration Layer
        config_layout = QHBoxLayout()
        self.sec_level = QComboBox()
        self.sec_level.addItems(["Level 1: Unencrypted", "Level 2: Quantum-aided AES", "Level 3: One-Time Pad"])
        config_layout.addWidget(QLabel("Security Configuration Tiers:"))
        config_layout.addWidget(self.sec_level)
        layout.addLayout(config_layout)
        
        # Addressing fields
        self.to_addr = QLineEdit()
        self.to_addr.setPlaceholderText("Recipient Email (e.g., node_b@yahoo.com)")
        layout.addWidget(QLabel("To:"))
        layout.addWidget(self.to_addr)
        
        self.subject = QLineEdit()
        self.subject.setPlaceholderText("Email Subject Header")
        layout.addWidget(QLabel("Subject:"))
        layout.addWidget(self.subject)
        
        # Message Workspace
        self.message_body = QTextEdit()
        self.message_body.setPlaceholderText("Compose message layer parameters...")
        layout.addWidget(QLabel("Message Workspace:"))
        layout.addWidget(self.message_body)
        
        # Execution Controls
        self.send_btn = QPushButton("Encrypt & Broadcast Message")
        self.send_btn.clicked.connect(self.process_and_transmit)
        layout.addWidget(self.send_btn)
        
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        
    def process_and_transmit(self):
        level = self.sec_level.currentIndex() + 1
        raw_text = self.message_body.toPlainText()
        
        if not raw_text:
            QMessageBox.warning(self, "Validation Alert", "Message body cannot be empty.")
            return
            
        try:
            # Query active local simulation keys
            km_data = self.km_client.fetch_next_available_key()
            key_id = km_data["key_id"]
            key_hex = km_data["key_hex"]
            
            iv_out = ""
            if level == 1:
                encrypted_bytes = CryptoVault.encrypt_level_1(raw_text)
            elif level == 2:
                encrypted_bytes, iv = CryptoVault.encrypt_level_2(raw_text, key_hex)
                iv_out = iv.hex()
            elif level == 3:
                encrypted_bytes = CryptoVault.encrypt_level_3_otp(raw_text, key_hex)
                
            payload_hex = encrypted_bytes.hex()
            
            # Note: For your live execution demo replace authentication credentials cleanly
            success = EmailEngine.send_quantum_email(
                smtp_server="://gmail.com", port=587,
                user="your_sihtesting_email@gmail.com", password="your_app_password",
                to_email=self.to_addr.text(), subject=self.subject.text(),
                payload_hex=payload_hex, level=level, key_id=key_id, iv_hex=iv_out
            )
            
            if success:
                QMessageBox.information(self, "Success Infrastructure Logs", f"Dispatched via Level {level} Security!\nUsing Key Reference: {key_id}")
        except Exception as err:
            QMessageBox.critical(self, "System Exception", f"Execution Fault: {str(err)}")

