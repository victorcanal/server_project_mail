import os
import datetime
import sqlite3
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
# from getpass import getpass


# clara.rabouan@gmail.com


IMAP_DICT = {
    "gmail": ("imap.gmail.com", 993),
    "aol": ("imap.aol.com ", 993),
    "outlook": ("imap-mail.outlook.com", 993),
    "yahoo": ("imap.mail.yahoo.com", 993),
    "free": ("imap.free.fr", 143),
    "laposte": ("imap.laposte.net", 993)
}
SMTP_DICT = {
    "gmail": ("smtp.gmail.com", 587),
    "aol": ("smtp.aol.com", 587),
    "outlook": ("smtp-mail.outlook.com", 587),
    "yahoo": ("smtp.mail.yahoo.com", 465),
    "free": ("smtp.free.fr", 25),
    "laposte": ("smtp.laposte.net", 587)
}


def clear(): 
    if os.name == 'nt': 
        _ = os.system('cls') 
    else: 
        _ = os.system('clear')


def login():
    while True:
        print("Enter your credentials:\n")
        _user_address = None
        while True:
            _user_address = input("Mail address: ")
            if re.match(r"([^.@]+)(\.[^.@]+)*@([^.@]+\.)+([^.@]+)", _user_address):
                break
            else:
                print("Wrong format of mail")
        password = input("Password: ")  # getpass("Password: ")
        mail_server = _user_address.split('@')[1].split('.')[0]
        imap_addr = IMAP_DICT.get(mail_server, "No imap server address associated.")
        smtp_addr = SMTP_DICT.get(mail_server, "No smtp server address associated.")
        if isinstance(imap_addr, tuple) and isinstance(smtp_addr, tuple):
            break
        else:
            print("This email address isn't supported.")

    # print(mail,password, imap_addr,smtp_addr)
    clear()
    # print("Credentials saved.")
    # return mail, password, imap_addr, smtp_addr

    # TODO: Try catch for if credentials are wrong
    _imap_connection = imaplib.IMAP4_SSL(imap_addr[0])
    _imap_connection.login(_user_address, password)

    _smtp_connection = smtplib.SMTP(smtp_addr[0], smtp_addr[1])
    _smtp_connection.ehlo()
    _smtp_connection.starttls()
    _smtp_connection.ehlo()
    _smtp_connection.login(_user_address, password)

    return _user_address, _imap_connection, _smtp_connection


def logout():
    imap_connection.logout()
    smtp_connection.quit()


def db_init():
    conn = sqlite3.connect('mails.db')
    c = conn.cursor()
    # c.execute('''DROP TABLE IF EXISTS mails''')
    # c.execute('''DROP TABLE IF EXISTS accounts''')
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (account_address VARCHAR(256) NOT NULL PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS mails (
        mail_id VARCHAR(256) NOT NULL PRIMARY KEY,
        mail_from TEXT,
        mail_to_list TEXT,
        mail_subject TEXT,
        mail_content TEXT,
        mail_attachment_list TEXT,
        mail_date DATETIME,
        mail_is_outbound BOOL,
        account_address VARCHAR(256),
        FOREIGN KEY (account_address) REFERENCES accounts(account_address))''')
    # c.execute('''ALTER TABLE accounts ADD CONSTRAINT PK_accounts PRIMARY KEY (account_address)''')
    # c.execute('''ALTER TABLE mails ADD CONSTRAINT PK_mails PRIMARY KEY (mail_id)''')
    # c.execute('''ALTER TABLE mails
    #     ADD CONSTRAINT FK_mails_account_address
    #     FOREIGN KEY (account_address)
    #     REFERENCES accounts (account_address)''')

    # c.execute("INSERT INTO mails VALUES (" +
    #           "'marcel.dupont@free.fr'," +
    #           "'clara.rabouan@gmail.com'," +
    #           "'Sujet intéressant'," +
    #           "'Bla bla bla texte texte'," +
    #           "'image.png'," +
    #           "'2020-12-14 20:22:30.500')")
    conn.commit()
    conn.close()


def retrieve():  # connection ssl to an imap server

    imap_connection.select('inbox')
    status, data = imap_connection.search(None, 'ALL')
    mail_ids = []
    for block in data:
        mail_ids += block.split()

    for i in mail_ids:
        status, data = imap_connection.fetch(i, '(RFC822)')

        for response_part in data:
            if isinstance(response_part, tuple):
                message = email.message_from_bytes(response_part[1])

                # print('Mail number ' + str(i))
                # for key in message:
                #     print(key)
                # print("#############################################")

                mail_id = message['message-id']
                print(mail_id)
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
                mail_is_outbound = False

                sqlite_db = sqlite3.connect('mails.db')
                c = sqlite_db.cursor()

                # TODO: Verify if id isn't already in database

                c.execute("INSERT INTO mails VALUES ('" +
                          mail_id + "','" +
                          mail_from + "','" +
                          mail_to + "','" +
                          mail_subject + "','" +
                          mail_content + "','" +
                          mail_attachments + "','" +
                          mail_date + "'," +
                          str(int(mail_is_outbound)) + ",'" +
                          user_address + "')")
                sqlite_db.commit()
                sqlite_db.close()


def read():
    conn = sqlite3.connect('mails.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM mails ORDER BY mail_date'):
        print(row)
    conn.close()


    # TODO: In send, make it so that the user can import a text file for the mail's text part


def send():
    response = "n"
    to = None
    subject = None
    content = None
    while response.lower() != "y":
        flag = True
        while flag:
            to = input("Enter the email of destination:\n")
            if re.match(r"([^.@]+)(\.[^.@]+)*@([^.@]+\.)+([^.@]+)", to):
                flag = False
            else:
                print("E-mail is not of a good format")
        subject = input("Enter the subject of your email: ")
        content = input("Write your email: ")
        print("From: " + user_address + "\n" +
              "To: " + to + "\n" +
              "Subject: " + subject + "\n" +
              " --- Content --- \n" + content + "\n")
        response = input("Send the e-mail?[y/n]")
    msg = MIMEMultipart()
    msg['From'] = user_address
    msg['To'] = to
    msg['Subject'] = subject
    message = content
    msg.attach(MIMEText(message))
    smtp_connection.sendmail(user_address, to, msg.as_string())
    print("Mail send successfully!!\n")


def menu(case: int):
    switch = {
        1: retrieve,
        2: send,
        3: read,
        4: logout
    }
    func = switch.get(case, lambda: print("Error : The given answer is not in the list."))
    func()


if __name__ == '__main__':
    while True:
        clear()
        user_address, imap_connection, smtp_connection = login()
        db_init()
        retrieve()

        # TODO: After logging out, send the user back to login
        # TODO: In read : sort mails
        # TODO: Save mails to .imf format files

        print("Menu:")
        entry_names = ["Refresh database", "Send", "Read", "Logout"]

        entry_number = -1
        while True:
            if entry_number == 4:
                break
            for i in range(len(entry_names)):
                print(str(i + 1) + ": " + entry_names[i])

            try:
                print("Desired menu entry number: ")
                entry_number = int(input())

                menu(entry_number)
            except ValueError:
                print("Error: The given answer is not a number.")
