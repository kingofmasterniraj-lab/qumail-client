# src/gui/main_window.py
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QTextEdit, QLineEdit, QComboBox, QPushButton, QMessageBox, QTabWidget)
from src.core.crypto_vault import CryptoVault
from src.core.key_manager_api import KeyManagerClient
from src.core.email_engine import EmailEngine
from src.core.email_receiver import EmailReceiverEngine

class QuMailWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuMail - Quantum Secure Email Client Workspace")
        self.setGeometry(100, 100, 800, 600)
        self.km_client = KeyManagerClient()
        self.receiver_engine = EmailReceiverEngine()
        
        # Core user configuration states (Change these parameters safely for your live presentation)
        self.email_user = "your_sihtesting_email@gmail.com"
        self.email_password = "your_app_password" # Use standard App Passwords for third-party security clients

        self.init_ui()
        
    def init_ui(self):
        tabs = QTabWidget()
        tabs.addTab(self.create_compose_tab(), "Compose Quantum Mail")
        tabs.addTab(self.create_inbox_tab(), "Secure Quantum Inbox")
        self.setCentralWidget(tabs)

    def create_compose_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Configuration Selection Layer
        config_layout = QHBoxLayout()
        self.sec_level = QComboBox()
        self.sec_level.addItems(["Level 1: No Quantum Security", "Level 2: Quantum-aided AES-256", "Level 3: Quantum Secure (One-Time Pad)"])
        config_layout.addWidget(QLabel("Security Profile:"))
        config_layout.addWidget(self.sec_level)
        layout.addLayout(config_layout)
        
        # Addressing fields
        self.to_addr = QLineEdit()
        self.to_addr.setPlaceholderText("Recipient address (e.g., node_b@yahoo.com)")
        layout.addWidget(QLabel("To Recipient:"))
        layout.addWidget(self.to_addr)
        
        self.subject = QLineEdit()
        self.subject.setPlaceholderText("Message Subject Line")
        layout.addWidget(QLabel("Subject Header:"))
        layout.addWidget(self.subject)
        
        # Message Payload Input Frame
        self.message_body = QTextEdit()
        self.message_body.setPlaceholderText("Write your secret payload message here...")
        layout.addWidget(QLabel("Email Text Payload Content:"))
        layout.addWidget(self.message_body)
        
        # Actions
        send_btn = QPushButton("Encrypt and Transmit Secure Mail Package")
        send_btn.clicked.connect(self.process_and_transmit)
        layout.addWidget(send_btn)
        
        widget.setLayout(layout)
        return widget

    def create_inbox_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Action Control Line
        fetch_btn = QPushButton("Fetch, Analyze, and Decrypt Latest Incoming Mail")
        fetch_btn.clicked.connect(self.fetch_and_parse_inbox)
        layout.addWidget(fetch_btn)
        
        # Meta Display Data Fields
        self.meta_label = QLabel("Active Hardware Key Tracker Logs: Clear")
        self.meta_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.meta_label)

        # Subject Line View Box
        self.inbox_subject_view = QLineEdit()
        self.inbox_subject_view.setReadOnly(True)
        layout.addWidget(QLabel("Parsed Subject Header:"))
        layout.addWidget(self.inbox_subject_view)

        # Message Reader Frame
        self.inbox_body_view = QTextEdit()
        self.inbox_body_view.setReadOnly(True)
        layout.addWidget(QLabel("Decrypted Workspace View Terminal:"))
        layout.addWidget(self.inbox_body_view)
        
        widget.setLayout(layout)
        return widget

    def process_and_transmit(self):
        level = self.sec_level.currentIndex() + 1
        raw_text = self.message_body.toPlainText()
        
        if not raw_text or not self.to_addr.text():
            QMessageBox.warning(self, "Input Check Error", "Recipient target information and message content fields are required.")
            return
            
        try:
            # Query Key Manager Client logic systems
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
            
            success = EmailEngine.send_quantum_email(
                smtp_server="://gmail.com", port=587,
                user=self.email_user, password=self.email_password,
                to_email=self.to_addr.text(), subject=self.subject.text(),
                payload_hex=payload_hex, level=level, key_id=key_id, iv_hex=iv_out
            )
            
            if success:
                QMessageBox.information(self, "Infrastructure Action Logged", f"Email successfully broadcast!\nUsed QKD Key Sync Index: {key_id}")
        except Exception as err:
            QMessageBox.critical(self, "System Routing Exception", f"Process Execution Interrupted: {str(err)}")

    def fetch_and_parse_inbox(self):
        self.inbox_body_view.setPlainText("Establishing handshake connection to standard incoming email server routing tunnels...")
        
        # Execute decryption pipeline over IMAP
        messages = self.receiver_engine.fetch_and_decrypt_latest(self.email_user, self.email_password)
        if messages:
            latest = messages[0]
            self.inbox_subject_view.setText(latest.get("subject", ""))
            self.inbox_body_view.setPlainText(latest.get("body", ""))
            self.meta_label.setText(f"Active Hardware Key Tracker Logs: {latest.get('meta', 'None')}")
