import os
import shutil
import smtplib
import ssl
import time
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SOURCE_FOLDER = "databasespython"    
BACKUP_FOLDER = "backups"       

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')

def send_email(subject, body):
    try:
        message = EmailMessage()
        message["From"] = EMAIL_SENDER
        message["To"] = EMAIL_RECEIVER
        message["Subject"] = subject
        message.set_content(body)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(message)
        
        logging.info(f"mail đã gửi: {subject}")
    except Exception as e:
        logging.error(f" Lỗi mail: {str(e)}")
        raise

def wait_until_next_target_time():
    now = datetime.now()
    target_time = datetime(now.year, now.month, now.day, 18, 49)
    if now > target_time:
        target_time = target_time.replace(day=now.day + 1)
    sleep_time = (target_time - now).total_seconds()
    logging.info(f" {target_time.strftime('%H:%M:%S')} {sleep_time} ")
    time.sleep(sleep_time)

def backup_databases():
    try:
        wait_until_next_target_time()
        if not os.path.exists(SOURCE_FOLDER):
            raise Exception(f"Không tìm thấy thư mục nguồn: {SOURCE_FOLDER}")
        if not os.path.exists(BACKUP_FOLDER):
            os.makedirs(BACKUP_FOLDER)
        files = os.listdir(SOURCE_FOLDER)
        db_files = [f for f in files if f.endswith('.sql') or f.endswith('.sqlite3')]

        if not db_files:
            raise Exception("Không tìm thấy file .sql hoặc .sqlite3 để backup.")
        for file_name in db_files:
            src_path = os.path.join(SOURCE_FOLDER, file_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file_name = f"{os.path.splitext(file_name)[0]}_{timestamp}{os.path.splitext(file_name)[1]}"
            dst_path = os.path.join(BACKUP_FOLDER, backup_file_name)
            shutil.copy2(src_path, dst_path)
            logging.info(f"File {file_name} backed qua {backup_file_name}.")
        #thanhcongggg
        logging.info("Backup thanhcong.")
        send_email("Backup Thành Công", f"Đã backup {len(db_files)} file database thành công lúc {datetime.now()}.")
    except Exception as e:
        #loi
        logging.error(f"Error occurred: {str(e)}")
        send_email("Backup Thất Bại", f"Lỗi khi backup database: {str(e)}")
if __name__ == "__main__":
    backup_databases()

