import smtplib
import imaplib
import email
import os

def sendEmail():
    print("Kirim Email")
    print("=*20")
    sender_email = input("Masukkan alamat email pengirim: ")
    receiver_email = input("Masukkan alamat email penerima: ")
    subject = input("Masukkan subjek email: ")
    body = input("Masukkan isi email: ")
    print("=*20")
    password = input("Masukkan kata sandi email pengirim: ")
    print("Mengirim email...")
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender_email, receiver_email, message)
        print("Email berhasil dikirim!")
    except Exception as e:
        print(f"Gagal mengirim email: {e}") #error Handling: Jika gagal mengirim email


def readEmail():
    print("Baca Email")
    print("=*20")
    



def main():
    print("=*20")
    print("Selamat Datang di Program Pengiriman Email")
    print("=*20")
    print("1. Kirim Email")
    print("2. Baca Email")
    print("3. Keluar")
    choice = input("Masukkan pilihan Anda (1/2/3): ")
    print("=*20")

    if choice == '1':
        sendEmail()
    elif choice == '2':
        readEmail()
    elif choice == '3':
        print("Terima kasih telah menggunakan program ini. Sampai jumpa!")
        exit()
    else:
        print("Pilihan tidak valid. Silakan coba lagi.")
        main() #Error Handling: Jika pilihhan tidak valid






