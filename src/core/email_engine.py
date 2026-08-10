
# src/core/email_receiver.py
import imaplib
import email
from email.header import decode_header
from src.core.crypto_vault import CryptoVault
from src.core.key_manager_api import KeyManagerClient

class EmailReceiverEngine:
    def __init__(self, imap_server="://gmail.com", port=993):
        self.imap_server = imap_server
        self.port = port
        self.km_client = KeyManagerClient()

    def fetch_and_decrypt_latest(self, user_email, password):
        """Connects to the inbox, reads the latest email, and runs quantum decryption."""
        results = []
        try:
            # Connect over SSL
            mail = imaplib.IMAP4_SSL(self.imap_server, self.port)
            mail.login(user_email, password)
            mail.select("inbox")

            # Search for all emails
            status, messages = mail.search(None, "ALL")
            if status != "OK" or not messages[0]:
                return [{"subject": "No Mail", "body": "Inbox is empty."}]

            # Get the list of message IDs and select the most recent one
            mail_ids = messages[0].split()
            latest_id = mail_ids[-1]

            # Fetch the email payload
            status, data = mail.fetch(latest_id, "(RFC822)")
            if status != "OK":
                return [{"subject": "Error", "body": "Could not fetch message data."}]

            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Decode Subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")

            # Extract Text Body Parts
            body_text = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disp = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_disp:
                        body_text = part.get_payload(decode=True).decode("utf-8")
                        break
            else:
                body_text = msg.get_payload(decode=True).decode("utf-8")

            # Process Quantum Decryption if our signature metadata tags match
            if "---QUMAIL-SECURE-PAYLOAD---" in body_text:
                parsed_data = self._parse_metadata(body_text)
                level = int(parsed_data.get("LEVEL", 1))
                key_id = parsed_data.get("KEY_ID", "")
                iv_hex = parsed_data.get("IV", "")
                ciphertext_hex = parsed_data.get("DATA", "").strip()

                # Fetch synchronized historical decryption key from local QKD buffer simulation
                qkd_key_hex = self.km_client.fetch_specific_key(key_id)
                ciphertext_bytes = bytes.fromhex(ciphertext_hex)

                # Decrypt according to target layer parameters
                if level == 1:
                    decrypted_text = CryptoVault.decrypt_level_1(ciphertext_bytes)
                elif level == 2:
                    iv_bytes = bytes.fromhex(iv_hex)
                    decrypted_text = CryptoVault.decrypt_level_2(ciphertext_bytes, qkd_key_hex, iv_bytes)
                elif level == 3:
                    decrypted_text = CryptoVault.decrypt_level_3_otp(ciphertext_bytes, qkd_key_hex)
                else:
                    decrypted_text = "[Error] Unknown encryption level configuration."

                results.append({
                    "subject": f"🔓 [Decrypted L{level}] {subject}",
                    "body": decrypted_text,
                    "meta": f"Key Used: {key_id}"
                })
            else:
                # Normal unencrypted fallback view for non-quantum system emails
                results.append({
                    "subject": subject,
                    "body": body_text,
                    "meta": "Standard Communication (No Quantum Metadata Tags)"
                })

            mail.logout()
        except Exception as err:
            results.append({"subject": "Connection Error", "body": f"Failed to fetch mail: {str(err)}", "meta": "None"})
        
        return results

    def _parse_metadata(self, text):
        """Helper to extract cryptographic attributes out of the raw text mail bundle."""
        metadata = {}
        lines = text.split("\n")
        for line in lines:
            if ":" in line:
                key, val = line.split(":", 1)
                metadata[key.strip()] = val.strip()
        return metadata
