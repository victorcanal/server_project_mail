import datetime
import sqlite3
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re


def db_init():
    conn = sqlite3.connect('mails.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mails (
        mail_from TEXT NOT NULL,
        mail_to_list TEXT NOT NULL,
        mail_subject TEXT,
        mail_content TEXT,
        mail_attachment_list TEXT,
        mail_date DATETIME NOT NULL)''')
    # c.execute("INSERT INTO mails VALUES (" +
    #           "'marcel.dupont@free.fr'," +
    #           "'clara.rabouan@gmail.com'," +
    #           "'Sujet intéressant'," +
    #           "'Bla bla bla texte texte'," +
    #           "'image.png'," +
    #           "'2020-12-14 20:22:30.500')")
    conn.commit()
    conn.close()


def retrieve(user_address: str, user_password: str, server_adress: str):
    # EMAIL = 'clara.rabouan@gmail.com'
    # PASSWORD = 'claradu77'
    # SERVER = 'imap.gmail.com'

    ssl_connection = imaplib.IMAP4_SSL(server_adress)
    ssl_connection.login(user_address, user_password)
    ssl_connection.select('inbox')
    status, data = ssl_connection.search(None, 'ALL')
    mail_ids = []
    for block in data:
        mail_ids += block.split()

    for i in mail_ids:
        status, data = ssl_connection.fetch(i, '(RFC822)')

        for response_part in data:
            if isinstance(response_part, tuple):
                message = email.message_from_bytes(response_part[1])

                mail_from = message['from']
                mail_to = message['to']
                mail_subject = message['subject']
                mail_date = str(datetime.datetime.now())

                if message.is_multipart():
                    mail_content = ''

                    for part in message.get_payload():
                        if part.get_content_type() == 'text/plain':
                            mail_content += part.get_payload()
                else:
                    mail_content = message.get_payload()

                mail_attachments = ''

                sqlite_db = sqlite3.connect('mails.db')
                c = sqlite_db.cursor()
                c.execute("INSERT INTO mails VALUES ('" +
                          mail_from + "','" +
                          mail_to + "','" +
                          mail_subject + "','" +
                          mail_content + "','" +
                          mail_attachments + "','" +
                          mail_date + "')")
                sqlite_db.commit()
                sqlite_db.close()
    ssl_connection.logout()


def read():
    conn = sqlite3.connect('mails.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM mail ORDER BY source'):
        print(row)
    conn.close()


def send():
    response="n"
    while(response.lower()!="y"):
        flag =True
        while(flag):
            destination=input("Enter the email of destination:\n")
            if re.match(r"([^.@]+)(\.[^.@]+)*@([^.@]+\.)+([^.@]+)", destination):
                flag=False
            else:
                print("Wrong format of mail")
        subject=input("Enter the subject of your email:\n")
        data=input("Write your email:\n")
        print("From:clara.rabouan@gmail.com\nTo: "+destination+"\nSubject: "+subject+"\nContent: "+data+"\n")
        response=input("Send the mail?[y/n]")
    msg = MIMEMultipart()
    msg['From'] = 'clara.rabouan@gmail.com'
    msg['To'] = destination
    msg['Subject'] = subject
    message = data
    msg.attach(MIMEText(message))
    mailserver = smtplib.SMTP('smtp.gmail.com',587)
    mailserver.ehlo()
    mailserver.starttls()
    mailserver.ehlo()
    mailserver.login('clara.rabouan@gmail.com', 'claradu77')
    mailserver.sendmail('clara.rabouan@gmail.com', destination, msg.as_string())
    mailserver.quit()


def menu(case: int):
    switch = {
        1: read,
        2: send,
        3: retrieve
    }
    func = switch.get(case, lambda: print("Error : The given answer is not in the list."))
    func()


if __name__ == '__main__':
    db_init()

    print("Menu:")
    entry_names = ["Read", "Send", "Retrieve"]

    for i in range(len(entry_names)):
        print(str(i + 1) + ": " + entry_names[i])

    entry_number = -1
    while True:
        try:
            print("Desired menu entry number: ")
            entry_number = int(input())

            menu(entry_number)
        except ValueError:
            print("Error: The given answer is not a number.")

