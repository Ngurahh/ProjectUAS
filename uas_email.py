import smtplib
import imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Konfigurasi
smtp_server = "smtp.gmail.com"
smtp_port = 587
imap_server = "imap.gmail.com"
imap_port = 993

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
            while True:
                email_address = input("Masukkan alamat email Anda: ")
                email_password = input("Masukkan sandi email Anda: ")
                try:
                    print("Mencoba masuk...")
                    server_smtp = smtplib.SMTP(smtp_server, smtp_port)
                    server_smtp.starttls()
                    server_smtp.login(email_address, email_password)
                    server_imap = imaplib.IMAP4_SSL(host=imap_server, port=imap_port)
                    server_imap.login(email_address, email_password)
                    print("Masuk berhasil!")
                    menu(email_address, server_smtp, server_imap)
                    break
                except smtplib.SMTPAuthenticationError:
                    print("Gagal login! Alamat atau sandi email salah.")
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
    while True:
        print('''================================
              Menu
================================
1. Kirim Email
2. Kotak Masuk
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
    while True:
        print('''================================
         Kirim Email
================================''')
        try:
            recipient = input("Masukkan alamat email penerima: ")
            subject = input("Masukkan subjek email: ")
            body = input("Masukkan isi email: ")

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

            print("Mengirimkan email...")
            server_smtp.sendmail(email_address, recipient, message.as_string())
            print("Email berhasil dikirim!")
        except Exception as e:
            print(f"Gagal mengirim email: {e}")
        ulang = input("Ingin mengirim email kembali? (y/n): ").strip().lower()
        if ulang != 'y':
            break

auth()
