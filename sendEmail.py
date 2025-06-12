import smtplib
import imaplib
from configuration import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def auth():
    while True:
        print('''================================
Selamat Datang di Program Email!
================================
1. Masuk
2. Keluar
--------------------------------''')
        option_auth = input("Pilihan anda (1/2): ")
        if option_auth == "1":
            while True:
                email_address = input("Masukkan alamat email Anda: ")
                email_password = input("Masukkan sandi email Anda: ")
                try:
                    print("Mencoba masuk...")
                    server_smtp = smtplib.SMTP(smtp_server, smtp_port)
                    server_imap = imaplib.IMAP4_SSL(host=imap_server, port=imap_port)
                    server_smtp.starttls()
                    server_imap.login(email_address, email_password)
                    server_smtp.login(email_address, email_password)
                    print("Masuk berhasil!")
                    menu(email_address, server_smtp, server_imap)
                    break
                except:
                    continue_auth = input(f"Terjadi kesalahan saat masuk. Ingin mencoba lagi? (y/n): ").strip().lower()
                    if continue_auth != "y":
                        break
        elif option_auth == "2":
            print("Terima kasih telah menggunakan program ini. Sampai jumpa!")
            exit()
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")
        
def menu(email_address, server_smtp, server_imap):
    while True:
        print('''================================
              Menu
================================
1. Kirim Email
2. Kotak Masuk
3. Keluar Akun
--------------------------------''')
        option_menu = (input("Pilihan anda (1/2/3): "))
        if option_menu == "1":
            sendEmail(email_address, server_smtp)
            break
        elif option_menu == "2":
            print("Kotak masuk")
            break
        elif option_menu == "3":
            print(f"Anda telah keluar dari akun {email_address}")
            server_smtp.quit()
            server_imap.close()
            server_imap.logout()
            auth()
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

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

            print("Mengirimkan email...")
            server_smtp.sendmail(email_address, recipient, message.as_string())
            print("Email berhasil dikirim!")

        except:
            option_continue2 = input(f"Gagal mengirimkan email. Ingin mencoba lagi? (y/n): ").strip().lower()
            if option_continue2 != 'y':
                menu()
                break

        option_continue2 = input("Apakah Anda ingin mengirim email lagi? (y/n): ").strip().lower()
        if option_continue2 != 'y':
            menu()
            break

# def recvEmail():

auth()