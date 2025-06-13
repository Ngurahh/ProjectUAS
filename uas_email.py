import smtplib
import imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import re
from getpass import getpass
from email import encoders

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
# Fungsi ini menangani proses autentikasi pengguna yang ingin mengakses program email
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
            try:
                print("Mencoba masuk ke akun email...")
                server_smtp = smtplib.SMTP(smtp_server, smtp_port)
                server_smtp.starttls()
                server_smtp.login(email_address, app_password)
                server_imap = imaplib.IMAP4_SSL(imap_server, imap_port)
                server_imap.login(email_address, app_password)
                print("Berhasil masuk ke akun email.")
                menu(email_address, server_smtp, server_imap)
                break
            except smtplib.SMTPAuthenticationError:
                print("Autentikasi gagal. Pastikan alamat email dan sandi Anda benar.")
            except imaplib.IMAP4.error as e:
                print(f"Gagal masuk ke akun IMAP: {e}")
            except Exception as e:
                print(f"Gagal terhubung ke server: {e}")    
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
        print("Gagal memuat kotak masuk. Silakan coba lagi.")
        return
    email_ids = messages[0].split()
    """ Fungsi ini menampilkan menu utama setelah pengguna berhasil masuk ke akun email mereka"""
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
            print("Fitur kotak masuk belum tersedia.")
        elif menu_option == "3":
            print(f"Anda telah keluar dari akun {email_address}")
            server_smtp.quit()
            server_imap.logout()
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

# Fungsi Kirim Email

def sendEmail(email_address, server_smtp):
    """ Fungsi ini menangani pengiriman email dengan opsi untuk menambahkan Penerima, subjek, isi, dan lampiran"""
    while True:
        print('''================================
         Kirim Email
================================''')
        """ Aku nambah validasi untuk penerima, subjek, dan isi email"""
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
                try:
                    with open(filename, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename={filename.split('/')[-1]}")
                        message.attach(part)
                    print(f"Lampiran {filename} berhasil ditambahkan.")
                except FileNotFoundError:
                    print(f"File {filename} tidak ditemukan. Silakan coba lagi.")
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

        ulang = input("Ingin mengirim email kembali? (y/n): ").strip().lower()
        if ulang != 'y':
            break

if __name__ == "__main__":
    auth()