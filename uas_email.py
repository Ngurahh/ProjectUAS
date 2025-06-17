from email_needs import *

# Fungsi untuk memecahkan kode header email dengan aman
def decodeMineHeader(header_value):
    decoded, encoding = decode_header(header_value)[0]
    if isinstance(decoded, bytes):
        try:
            return decoded.decode(encoding if encoding else 'utf-8', errors='ignore')
        except Exception:
            return decoded.decode('utf-8', errors='ignore')
    return decoded

# fungsi untuk memecahkan kode badan email dengan aman
def decodeEmailBody(part):
    try:
        body = part.get_payload(decoded=True)
        return body.decode('utf-8', errors='ignore')
    except Exception:
        return ""

# fungsi untuk menyimpan lampiran dan mengembalikan daftar nama file yang disimpan
def saveAttachments(email_message):
    saved_filenames = []
    for part in email_message.walk():
        content_disposition = str(part.get("Content-Disposition", ""))
        if "attachment" in content_disposition:
            filename = part.get_filename()
            if filename:
                decoded_filename = decodeMineHeader(filename)
                try:
                    os.makedirs("unduhan", exist_ok=True)
                    filepath = os.path.join("unduhan", f"{round(time.time())}")
                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    saved_filenames.append(decoded_filename)
                    print(f"Lampiran disimpan di: {filepath}")
                except Exception as e:
                    print(f"Error menympan laimpran: {e}")
    return saved_filenames


# validasi email menggunakan regex
def validasiEmail(email_address):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email_address))

# fungsi untuk autentikasi dimana user memasukkan alamat email dan sandi
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

# fungsi menu yang menampilkan opsi yang dapat dilakukan oleh user ketika sudah berhasil masuk
def replyEmail(email_address, server_smtp, server_imap):
    try:
        server_imap.select("inbox")
        _, email_ids_raw = server_imap.search(None, "ALL")
        email_ids = email_ids_raw[0].split()

        if not email_ids:
            print("Tidak ada email di kotak masuk.")
            return

        email_ids = email_ids[-20:][::-1]
        emails = []

        for num in email_ids:
            try:
                _, email_data = server_imap.fetch(num, '(RFC822)')
                raw_email = email_data[0][1]
                email_info = email.message_from_bytes(raw_email)

                subject_raw = email_info.get('Subject', "(Tanpa Subjek)")
                decoded_subject, encoding = decode_header(subject_raw)[0]
                if isinstance(decoded_subject, bytes):
                    decoded_subject = decoded_subject.decode(encoding if encoding else 'utf-8', errors='ignore')

                # Hilangkan (Balasan) jika ada
                if decoded_subject.startswith("(Balasan) "):
                    decoded_subject = decoded_subject.replace("(Balasan) ", "")

                date_raw = email_info.get('Date', "(Tanpa Tanggal)")
                try:
                    parsed_date = parsedate_to_datetime(date_raw).astimezone(ZoneInfo("Asia/Makassar"))
                except:
                    parsed_date = datetime.min.replace(tzinfo=ZoneInfo("Asia/Makassar"))

                emails.append({
                    "id": num,
                    "from": email_info.get('From', "(Tanpa Pengirim)"),
                    "subject": decoded_subject,
                    "date": parsed_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "parsed_date": parsed_date,
                    "message_id": email_info.get("Message-ID"),
                    "email_info": email_info,
                })
            except:
                continue

        emails.sort(key=lambda x: x["parsed_date"], reverse=True)
        emails = emails[:20]

        while True:
            print("================================")
            print("          Balas Email ")
            print("================================")
            for i, email_item in enumerate(emails, 1):
                print(f"{i}. Dari   : {email_item['from']}")
                print(f"   Subjek : {email_item['subject']}")
                print(f"   Tanggal: {email_item['date']}")
                print("--------------------------------")

            try:
                reply_email_option = int(input("Masukkan id email untuk membalas (0 untuk kembali): ").strip())
                if reply_email_option == 0:
                    return
                elif 1 <= reply_email_option <= len(emails):
                    selected_email = emails[reply_email_option - 1]
                    email_message = selected_email["email_info"]

                    previous_body = ""
                    previous_filenames = []

                    if email_message.is_multipart():
                        for part in email_message.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition", ""))

                            if content_type in ["text/plain", "text/html"]:
                                try:
                                    body = part.get_payload(decode=True)
                                    decoded_body = body.decode('utf-8', errors='ignore')
                                    previous_body = decoded_body
                                except Exception as e:
                                    print(f"Error membaca isi email: {e}")
                            elif "attachment" in content_disposition:
                                filename = part.get_filename()
                                if filename:
                                    try:
                                        decoded_filename, encoding = decode_header(filename)[0]
                                        if isinstance(decoded_filename, bytes):
                                            decoded_filename = decoded_filename.decode(encoding if encoding else 'utf-8', errors='ignore')
                                        os.makedirs("unduhan", exist_ok=True)
                                        filepath = os.path.join("unduhan", f"{round(time.time())}_{decoded_filename}")
                                        with open(filepath, "wb") as f:
                                            f.write(part.get_payload(decode=True))
                                        previous_filenames.append(decoded_filename)
                                        print(f"Lampiran disimpan di: {filepath}")
                                    except Exception as e:
                                        print(f"Error menyimpan lampiran: {e}")
                    else:
                        try:
                            body = email_message.get_payload(decode=True)
                            decoded_body = body.decode('utf-8', errors='ignore')
                            previous_body = decoded_body
                        except Exception as e:
                            print(f"Error membaca isi email: {e}")

                    sendEmail(
                        email_address,
                        server_smtp,
                        recipient_address=email_message.get("From", ""),
                        original_subject=selected_email["subject"],
                        original_message_id=email_message.get("Message-ID"),
                        previous_body=previous_body,
                        previous_filenames=previous_filenames
                    )
                else:
                    print("Pilihan tidak valid. Silakan coba lagi.")
            except ValueError:
                print("Masukkan angka yang valid.")
    except Exception as e:
        print(f"Gagal membaca email: {e}")

def menu(email_address, server_smtp, server_imap):    
    while True:
        print('''================================
              Menu
================================
1. Kirim Email
2. Kotak Masuk
3. Balas Email
4. Keluar Akun
--------------------------------''')
        menu_option = input("Pilihan anda (1/2/3/4): ")
        if menu_option == "1":
            sendEmail(email_address, server_smtp)
        elif menu_option == "2":
            recvEmail(email_address, server_smtp, server_imap)
        elif menu_option == "3":
            replyEmail(email_address, server_smtp, server_imap)
        elif menu_option == "4":
            print(f"Anda telah keluar dari akun {email_address}")
            try:
                server_smtp.quit()
            except Exception:
                pass
            try:
                server_imap.close()
                server_imap.logout()
            except Exception:
                pass
            return
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

# fungsi untuk mengirim email
def sendEmail(email_address, 
              server_smtp, 
              recipient_address="", 
              original_subject=None, 
              original_message_id=None, 
              previous_body=None, 
              previous_filenames=None):
    while True:
        print("================================")
        print("          Kirim Email")
        print("================================")
        if not recipient_address:   
            recipient_address = input("Masukkan alamat email penerima: ")
        if not validasiEmail(recipient_address):
            print("Alamat email penerima tidak valid. Silakan coba lagi.")
            continue

        if original_subject:
            subject = f"(Balasan) {original_subject}"
            print(f"Subjek email: {original_subject}")
        else:
            while True:
                subject = input("Masukkan subjek email: ")
                if subject.strip():
                    break
                else:
                    print("Subjek tidak boleh kosong. Silakan coba lagi.")
                    continue

        print("Masukkan isi email:")
        body = input("> ")

        # Tambahkan isi email sebelumnya jika ada
        if previous_body:
            if "------ Email sebelumnya ------" in previous_body:
                clean_body = previous_body.replace("------ Email sebelumnya ------", "").strip()
            else:
                clean_body = previous_body.strip()
            body += "\n\n------ Email sebelumnya ------\n\n" + clean_body
            if previous_filenames:
                body += "\n\nLampiran sebelumnya:\n" + "\n".join(previous_filenames)

        # Siapkan pesan email
        message = MIMEMultipart()
        message["From"] = email_address
        message["To"] = recipient_address
        message["Subject"] = subject

        if original_message_id:
            message["In-Reply-To"] = original_message_id
            message["References"] = original_message_id

        message.attach(MIMEText(body, 'plain'))

        # Tambahkan lampiran baru jika ada
        add_attachment = input("Apakah Anda ingin menambahkan lampiran? (y/n): ").strip().lower()
        if add_attachment == 'y':
            while True:
                filename = input("Masukkan nama file lampiran (contoh: test.txt): ")
                if not filename.strip():
                    print("Nama file tidak boleh kosong.")
                    continue
                if not os.path.exists(filename):
                    print(f"File {filename} tidak ditemukan. Silakan coba lagi.")
                    continue
                try:
                        
                    with open(filename, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(filename)}")
                        message.attach(part)
                    print(f"Lampiran {filename} berhasil ditambahkan.")
                except Exception as e:
                    print(f"Gagal menambahkan lampiran: {e}")
                    continue
                    
                more = input("Apakah Anda ingin menambahkan lampiran lain? (y/n): ").strip().lower()
                if more != "y":
                    break

        # Kirim email
        try:
            print("Mengirimkan email...")
            server_smtp.sendmail(email_address, recipient_address, message.as_string())
            print("Email berhasil dikirim!")
        except Exception as e:
            print(f"Gagal mengirim email: {e}")

        if not original_message_id:
            more = input("Ingin mengirim email kembali? (y/n): ").strip().lower()
            if more != "y":
                return      
        return

# fungsi untuk menerima email
def recvEmail(email_address, server_smtp, server_imap):
    try:
        server_imap.select("inbox")
        _, email_ids_raw = server_imap.search(None, "ALL")
        email_ids = email_ids_raw[0].split()

        if not email_ids:
            print("Tidak ada email di kotak masuk.")
            return

        email_ids = email_ids[-20:][::-1]
        emails = []

        for num in email_ids:
            try:
                _, email_data = server_imap.fetch(num, '(RFC822)')
                raw_email = email_data[0][1]
                email_info = email.message_from_bytes(raw_email)

                subject_raw = email_info.get('Subject', "(Tanpa Subjek)")
                decoded_subject, encoding = decode_header(subject_raw)[0]
                if isinstance(decoded_subject, bytes):
                    decoded_subject = decoded_subject.decode(encoding if encoding else 'utf-8', errors='ignore')

                # Hilangkan (Balasan) jika ada
                if decoded_subject.startswith("(Balasan) "):
                    decoded_subject = "(Balasan) " + decoded_subject.replace("(Balasan) ", "")

                date_raw = email_info.get('Date', "(Tanpa Tanggal)")
                try:
                    parsed_date = parsedate_to_datetime(date_raw).astimezone(ZoneInfo("Asia/Makassar"))
                except:
                    parsed_date = datetime.min.replace(tzinfo=ZoneInfo("Asia/Makassar"))

                emails.append({
                    "id": num,
                    "from": email_info.get('From', "(Tanpa Pengirim)"),
                    "subject": decoded_subject,
                    "date": parsed_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "parsed_date": parsed_date,
                })
            except:
                continue

        emails.sort(key=lambda x: x["parsed_date"], reverse=True)
        emails = emails[:20]

        while True:
            print("================================")
            print("          Kotak Masuk ")
            print("================================")
            for i, email_item in enumerate(emails, 1):
                print(f"{i}. Dari   : {email_item['from']}")
                print(f"   Subjek : {email_item['subject']}")
                print(f"   Tanggal: {email_item['date']}")
                print("--------------------------------")

            try:
                read_email_option = int(input("Masukkan id email untuk melihat isi (0 untuk kembali): ").strip())
                if read_email_option == 0:
                    return
                elif 1 <= read_email_option <= len(emails):
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
                            decoded_subject = decoded_subject.replace("(Balasan) ", "")

                            # Tanggal isi email
                            date_raw = email_message.get("Date", "(Tanpa Tanggal)")
                            try:
                                parsed_date = parsedate_to_datetime(date_raw).astimezone(ZoneInfo("Asia/Makassar"))
                                formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                formatted_date = "(Tanggal tidak valid)"

                            print("================================")
                            print("           Isi Email")
                            print("================================")
                            print(f"Dari   : {email_message.get('From', '(Tanpa Pengirim)')}")
                            print(f"Subjek : {decoded_subject}")
                            print(f"Tanggal: {formatted_date}")
                            print("--------------------------------")

                            previous_body = ""
                            previous_filenames = []

                            if email_message.is_multipart():
                                for part in email_message.walk():
                                    content_type = part.get_content_type()
                                    content_disposition = str(part.get("Content-Disposition", ""))

                                    if content_type in ["text/plain", "text/html"]:
                                        try:
                                            body = part.get_payload(decode=True)
                                            decoded_body = body.decode('utf-8', errors='ignore')
                                            previous_body = decoded_body
                                            print(f"Isi Email:\n\n{decoded_body}")
                                        except Exception as e:
                                            print(f"Error membaca isi email: {e}")
                                    elif "attachment" in content_disposition:
                                        filename = part.get_filename()
                                        if filename:
                                            try:
                                                decoded_filename, encoding = decode_header(filename)[0]
                                                if isinstance(decoded_filename, bytes):
                                                    decoded_filename = decoded_filename.decode(encoding if encoding else 'utf-8', errors='ignore')
                                                os.makedirs("unduhan", exist_ok=True)
                                                filepath = os.path.join("unduhan", f"{round(time.time())}_{decoded_filename}")
                                                with open(filepath, "wb") as f:
                                                    f.write(part.get_payload(decode=True))
                                                previous_filenames.append(decoded_filename)
                                                print(f"Lampiran disimpan di: {filepath}")
                                            except Exception as e:
                                                print(f"Error menyimpan lampiran: {e}")
                            else:
                                try:
                                    body = email_message.get_payload(decode=True)
                                    decoded_body = body.decode('utf-8', errors='ignore')
                                    previous_body = decoded_body
                                    print(f"Isi Email:\n{decoded_body}")
                                except Exception as e:
                                    print(f"Error membaca isi email: {e}")

                            reply = input("Apakah anda ingin membalas email ini? (y/n): ").strip().lower()
                            if reply == "y":
                                sendEmail(
                                    email_address,
                                    server_smtp,
                                    recipient_address=email_message.get("From", ""),
                                    original_subject=decoded_subject,
                                    original_message_id=email_message.get("Message-ID"),
                                    previous_body=previous_body,
                                    previous_filenames=previous_filenames
                                )
                else:
                    print("Pilihan tidak valid. Silakan coba lagi.")
            except ValueError:
                print("Masukkan angka yang valid.")
    except Exception as e:
        print(f"Gagal membaca email: {e}")


if __name__ == "__main__":
    auth()

# email_password = 'ulbh lgzz fkfp zvtp'