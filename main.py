import datetime
import sqlite3
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def connect():
    conn = sqlite3.connect('mail.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE mail
                 (source text, destination text, data text, date datetime, text filepath)''')
    c.execute("INSERT INTO mail VALUES ('Dupont','Moi','Bonjour','2020-12-14 20:22:30.500','')")
    conn.commit()
    conn.close()


def retrieve():
    EMAIL = 'clara.rabouan@gmail.com'
    PASSWORD = 'claradu77'
    SERVER = 'imap.gmail.com'

    mail = imaplib.IMAP4_SSL(SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')
    status, data = mail.search(None, 'ALL')
    mail_ids = []
    for block in data:
        mail_ids += block.split()

    for i in mail_ids:
        status, data = mail.fetch(i, '(RFC822)')

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

                conn = sqlite3.connect('mail.db')
                c = conn.cursor()
                c.execute("INSERT INTO mail VALUES ('" + mail_from + "','" + mail_to + "','" + mail_content + "','" + mail_date + "',' ')")
                conn.commit()
                conn.close()


def read():
    conn = sqlite3.connect('mail.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM mail ORDER BY source'):
        print(row)
    conn.close()
    

def send():
    msg = MIMEMultipart()
    msg['From'] = 'clara.rabouan@gmail.com'
    msg['To'] = 'clara.rabouan@gmail.com'
    msg['Subject'] = 'Le sujet de mon mail' 
    message = 'Bonjour !'
    msg.attach(MIMEText(message))
    mailserver = smtplib.SMTP('smtp.gmail.com',587)
    mailserver.ehlo()
    mailserver.starttls()
    mailserver.ehlo()
    mailserver.login('clara.rabouan@gmail.com', 'claradu77')
    mailserver.sendmail('clara.rabouan@gmail.com', 'clara.rabouan@gmail.com', msg.as_string())
    mailserver.quit()


def function_one():
    return " --- Executing function_one"


def function_two():
    return " --- Executing function_two"


def function_three():
    return " --- Executing function_three"


def menu(case: int):
    switch = {
        1: read,
        2: send,
        3: retrieve
    }
    func = switch.get(case, lambda: print("Error : The given answer is not in the list."))
    func()


if __name__ == '__main__':
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

