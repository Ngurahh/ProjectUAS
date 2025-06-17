# Library yang diperlukan
import os
import re
import time
import email 
import smtplib
import imaplib
from email import encoders
from getpass import getpass
from zoneinfo import ZoneInfo
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.header import decode_header
from email.utils import parsedate_to_datetime
from email.mime.multipart import MIMEMultipart

# Konfigurasi server beserta port
smtp_server = "smtp.gmail.com"
smtp_port = 587
imap_server = "imap.gmail.com"
imap_port = 993