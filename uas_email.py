import os
import re
import time
import email 
import smtplib
import imaplib
from email import encoders
from getpass import getpass
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.header import decode_header
from email.mime.multipart import MIMEMultipart

# Konfigurasi
smtp_server = "smtp.gmail.com"
smtp_port = 587
imap_server = "imap.gmail.com"
imap_port = 993

# Fungsi Validasi Email
def validasiEmail(email_address):
    """ Fungsi ini memvalidasi format alamat email menggunakan regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email_address))

# Fungsi Autentikasi
def auth():
    while True:
        print('''================================
Selamat Datang di Program Email!
================================
1. Masuk
2. Keluar
--------------------------------''')
        auth_option = input("Pilihan anda (1/2): ")
        if auth_option == "1":
            email_address = input("Masukkan alamat email Anda: ")
            if not validasiEmail(email_address):
                print("Alamat email tidak valid. Silakan coba lagi.")
                continue
            app_password = getpass("Masukkan sandi email Anda (gunakan app password): ")
            if not app_password:
                print("Sandi tidak boleh kosong. Silakan coba lagi.")
                continue
            
            server_smtp = None
            server_imap = None
            try:
                print("Mencoba masuk ke akun email...")
                # Membuat koneksi ke server SMTP
                server_smtp = smtplib.SMTP(smtp_server, smtp_port)
                server_smtp.starttls()
                server_smtp.login(email_address, app_password)
                
                # Membuat koneksi ke server IMAP
                server_imap = imaplib.IMAP4_SSL(imap_server, imap_port)
                server_imap.login(email_address, app_password)
                
                print("Berhasil masuk ke akun email.")
                menu(email_address, server_smtp, server_imap)
            except smtplib.SMTPAuthenticationError:
                print("Autentikasi gagal. Pastikan alamat email dan sandi Anda benar.")
                continue
            except imaplib.IMAP4.error as e:
                print(f"Gagal masuk ke akun IMAP: {e}")
                continue
            except Exception as e:
                print(f"Gagal terhubung ke server: {e}")
                continue
        elif auth_option == "2":
            print("Terima kasih telah menggunakan program ini. Sampai jumpa!")
            exit()
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

# Fungsi Menu Utama
def menu(email_address, server_smtp, server_imap):
    server_imap.select("inbox")
    status, messages = server_imap.search(None, 'ALL')
    if status != 'OK':
        messages = "Gagal memuat kotak masuk"
    email_ids = messages[0].split()
        
    while True:
        print(f'''================================
              Menu
================================
1. Kirim Email
2. Kotak Masuk ({len(email_ids)} Email)
3. Keluar Akun
--------------------------------''')
        menu_option = input("Pilihan anda (1/2/3): ")
        if menu_option == "1":
            sendEmail(email_address, server_smtp)
        elif menu_option == "2":
            recvEmail(server_imap, email_ids)
        elif menu_option == "3":
            print(f"Anda telah keluar dari akun {email_address}")
            server_smtp.quit()
            server_imap.close()
            server_imap.logout()
            return
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

# Fungsi Kirim Email
def sendEmail(email_address, server_smtp):
    while True:
        print('''================================
         Kirim Email
================================''')
        
        recipient = input("Masukkan alamat email penerima: ")
        if not validasiEmail(recipient):
            print("Alamat email penerima tidak valid. Silakan coba lagi.")
            continue
        subject = input("Masukkan subjek email: ")
        if not subject.strip():
            print("Subjek tidak boleh kosong. Silakan coba lagi.")
            continue
        body = input("Masukkan isi email: ")
        if not body.strip():
            print("Isi email tidak boleh kosong. Silakan coba lagi.")
            continue

        message = MIMEMultipart()
        message["From"] = email_address
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(body, 'plain'))

        # Tambah Lampiran
        add_attachment = input("Apakah Anda ingin menambahkan lampiran? (y/n): ").strip().lower()
        if add_attachment == 'y':
            while True:
                filename = input("Masukkan nama file lampiran (contoh: test.txt): ")
                if not filename.strip():
                    print("Nama file tidak boleh kosong.")
                    continue
                try:
                    if not os.path.exists(filename):
                        print(f"File {filename} tidak ditemukan. Silakan coba lagi.")
                        continue
                        
                    with open(filename, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(filename)}")
                        message.attach(part)
                    print(f"Lampiran {filename} berhasil ditambahkan.")
                except PermissionError:
                    print(f"Tidak memiliki izin untuk membaca file {filename}.")
                    continue
                except Exception as e:
                    print(f"Gagal menambahkan lampiran: {e}")
                    continue
                    
                more = input("Apakah Anda ingin menambahkan lampiran lain? (y/n): ").strip().lower()
                if more != 'y':
                    break
        try:
            print("Mengirimkan email...")
            server_smtp.sendmail(email_address, recipient, message.as_string())
            print("Email berhasil dikirim!")
        except smtplib.SMTPException as e:
            print(f"Gagal mengirim email: {e}")
        except Exception as e:
            print(f"Gagal mengirim email: {e}")

        more = input("Ingin mengirim email kembali? (y/n): ").strip().lower()
        if more != 'y':
            return

# Fungsi Menerima Email
def recvEmail(server_imap):
    try:
        server_imap.select("inbox")
        _, message_numbers = server_imap.search(None, "ALL")
        email_ids = message_numbers[0].split()

        if not email_ids:
            print("Tidak ada email di kotak masuk.")
            return

        print(f'''================================
      Kotak Masuk ({len(email_ids)} Email)
================================''')

        # Mengambil 10 email terbaru (dibalik agar terbaru di atas)
        email_ids = email_ids[-10:][::-1]
        emails = []

        for num in email_ids:
            try:
                _, email_data = server_imap.fetch(num, '(RFC822)')
                email_info = email.message_from_bytes(email_data[0][1])
                subject_raw = email_info.get('Subject', "(Tanpa Subjek)")
                decoded_subject, encoding = decode_header(subject_raw)[0]
                if isinstance(decoded_subject, bytes):
                    decoded_subject = decoded_subject.decode(encoding if encoding else 'utf-8', errors='ignore')

                emails.append({
                    "id": num,
                    "from": email_info.get('From', "(Tanpa Pengirim)"),
                    "subject": decoded_subject,
                    "date": email_info.get('Date', "(Tanpa Tanggal)")
                })
            except Exception as e:
                print(f"Error membaca email {num}: {e}")
                continue

        if not emails:
            print("Tidak ada email yang dapat ditampilkan.")
            return

        # Menampilkan daftar email
        print("Daftar Email:")
        for i, email_item in enumerate(emails, 1):
            print(f"{i}. Dari: {email_item['from']} | Subjek: {email_item['subject']} | Tanggal: {email_item['date']}")

        # Pilih email untuk dibaca
        while True:
            try:
                read_email_option = int(input("Masukkan nomor email untuk melihat isi (0 untuk kembali): ").strip())
                if read_email_option == 0:
                    break
                if 1 <= read_email_option <= len(emails):
                    selected_email = emails[read_email_option - 1]
                    status, message_data = server_imap.fetch(selected_email["id"], '(RFC822)')
                    if status != 'OK':
                        print("Gagal mengambil email.")
                        continue

                    for response_part in message_data:
                        if isinstance(response_part, tuple):
                            email_message = email.message_from_bytes(response_part[1])
                            subject_raw = email_message.get("Subject", "(Tanpa Subjek)")
                            decoded_subject, encoding = decode_header(subject_raw)[0]
                            if isinstance(decoded_subject, bytes):
                                decoded_subject = decoded_subject.decode(encoding if encoding else 'utf-8', errors='ignore')

                            print("================================")
                            print("           Isi Email")
                            print("================================")
                            print(f"Dari   : {email_message.get('From', '(Tanpa Pengirim)')}")
                            print(f"Subjek : {decoded_subject}")
                            print(f"Tanggal: {email_message.get('Date', '(Tanpa Tanggal)')}")
                            print("--------------------------------")

                            if email_message.is_multipart():
                                for part in email_message.walk():
                                    content_type = part.get_content_type()
                                    content_disposition = str(part.get("Content-Disposition", ""))

                                    if content_type in ["text/plain", "text/html"]:
                                        try:
                                            body = part.get_payload(decode=True)
                                            print(f"Isi Email:\n{body.decode('utf-8', errors='ignore')}")
                                        except Exception as e:
                                            print(f"Error membaca isi email: {e}")

                                    elif "attachment" in content_disposition:
                                        filename = part.get_filename()
                                        if filename:
                                            try:
                                                decoded_filename, encoding = decode_header(filename)[0]
                                                if isinstance(decoded_filename, bytes):
                                                    decoded_filename = decoded_filename.decode(encoding if encoding else 'utf-8', errors='ignore')
                                                # os.makedirs("unduhan", exist_ok=True)
                                                filepath = os.path.join("unduhan", f"{round(time.time())}_{decoded_filename}")
                                                with open(filepath, "wb") as f:
                                                    f.write(part.get_payload(decode=True))
                                                print(f"Lampiran disimpan di: {filepath}")
                                            except Exception as e:
                                                print(f"Error menyimpan lampiran: {e}")
                            else:
                                try:
                                    body = email_message.get_payload(decode=True)
                                    print(f"Isi Email:\n{body.decode('utf-8', errors='ignore')}")
                                except Exception as e:
                                    print(f"Error membaca isi email: {e}")
                else:
                    print("Pilihan tidak valid.")
            except ValueError:
                print("Masukkan angka yang valid.")
    except imaplib.IMAP4.error as e:
        print(f"Gagal membaca email: {e}")
    except Exception as e:
        print(f"Gagal membaca email: {e}")

# Bagian utama untuk menjalankan program
if __name__ == "__main__":
    auth()