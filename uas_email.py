import smtplib
import imaplib
import email  # TAMBAHAN: Import yang hilang
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import re
from getpass import getpass
import os

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
            finally:
                if server_smtp:
                    try:
                        server_smtp.quit()
                    except:
                        pass
                if server_imap:
                    try:
                        server_imap.logout()
                    except:
                        pass
                        
        elif auth_option == "2":
            print("Terima kasih telah menggunakan program ini. Sampai jumpa!")
            exit()
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

# Fungsi Menu Utama
def menu(email_address, server_smtp, server_imap):
    try:
        server_imap.select("inbox")
        status, messages = server_imap.search(None, 'ALL')
        if status != 'OK':
            print("Gagal memuat kotak masuk. Silakan coba lagi.")
            return
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
                # PERBAIKAN: Memanggil fungsi rcvEmail
                rcvEmail(email_address, server_imap)
            elif menu_option == "3":
                print(f"Anda telah keluar dari akun {email_address}")
                break
            else:
                print("Pilihan tidak valid. Silakan coba lagi.")
    except Exception as e:
        print(f"Error dalam menu: {e}")
    finally:
        try:
            if server_smtp:
                server_smtp.quit()
        except:
            pass
        try:
            if server_imap:
                server_imap.logout()
        except:
            pass

# Fungsi Kirim Email
def sendEmail(email_address, server_smtp):
    """ Fungsi ini menangani pengiriman email dengan opsi untuk menambahkan Penerima, subjek, isi, dan lampiran"""
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

        ulang = input("Ingin mengirim email kembali? (y/n): ").strip().lower()
        if ulang != 'y':
            break

# Fungsi Menerima Email
def rcvEmail(email_address, server_imap):
    """Fungsi ini menampilkan email yang diterima"""
    print('''================================
         Kotak Masuk
================================''')
    try:
        server_imap.select('INBOX')
        _, message_numbers = server_imap.search(None, 'ALL')
        email_ids = message_numbers[0].split()
        if not email_ids:
            print("Tidak ada email di kotak masuk.")
            return

        # Mengambil 10 email terbaru
        email_ids = email_ids[-10:][::-1]
        emails = []
        for num in email_ids:
            try:
                _, msg_data = server_imap.fetch(num, '(RFC822)')
                email_message = email.message_from_bytes(msg_data[0][1])
                emails.append({
                    'id': num,
                    'from': email_message.get('From', "(Tanpa Pengirim)"),
                    'subject': email_message.get('Subject', "(Tanpa Subjek)"),
                    'date': email_message.get('Date', "(Tanpa Tanggal)")
                })
            except Exception as e:
                print(f"Error membaca email {num}: {e}")
                continue

        if not emails:
            print("Tidak ada email yang dapat ditampilkan.")
            return

        # Menampilkan Daftar Email
        print("Daftar Email:")
        for i, email_item in enumerate(emails, 1):
            print(f"{i}. Dari: {email_item['from']} | Subjek: {email_item['subject']} | Tanggal: {email_item['date']}")

        # Pilih email untuk dibaca
        try:
            rcvEmail_option = input("Masukkan nomor email untuk melihat isi (0 untuk kembali): ").strip()
            if rcvEmail_option == '0':
                return
                
            rcvEmail_option = int(rcvEmail_option)
            if 1 <= rcvEmail_option <= len(emails):
                selected_email = emails[rcvEmail_option - 1]
                _, msg_data = server_imap.fetch(selected_email['id'], '(RFC822)')
                email_message = email.message_from_bytes(msg_data[0][1])

                print("================================")
                print("Isi Email")
                print("================================")
                print(f"Dari: {email_message.get('From', '(Tanpa Pengirim)')}")
                print(f"Subjek: {email_message.get('Subject', '(Tanpa Subjek)')}")
                print(f"Tanggal: {email_message.get('Date', '(Tanpa Tanggal)')}")
                print("--------------------------------")

                content_found = False
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            try:
                                payload = part.get_payload(decode=True)
                                if payload:
                                    print("Isi Email:")
                                    print(payload.decode('utf-8', errors='ignore'))
                                    content_found = True
                                    break
                            except Exception as e:
                                print(f"Error membaca isi email: {e}")
                else:
                    try:
                        payload = email_message.get_payload(decode=True)
                        if payload:
                            print("Isi Email:")
                            print(payload.decode('utf-8', errors='ignore'))
                            content_found = True
                    except Exception as e:
                        print(f"Error membaca isi email: {e}")
                
                if not content_found:
                    print("Tidak dapat menampilkan isi email.")
                    
            else:
                print("Pilihan tidak valid.")
        except ValueError:
            print("Masukkan nomor yang valid.")
    except imaplib.IMAP4.error as e:
        print(f"Gagal membaca email: {e}")
    except Exception as e:
        print(f"Gagal membaca email: {e}")

if __name__ == "__main__":
    auth()