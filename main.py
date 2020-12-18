import os
from datetime import datetime
import sqlite3
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email import header
import re
import json
from getpass import getpass

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
SQL_ESCAPE_DICT = {
    "'": "\\'",
    '"': '\\"',
    '%': '\\%',
    '_': '\\_',
    '\n': '\\n',
    '\r': '\\r'
}
# \\: A backslash (\) character


def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


def log_connection(protocol: str, _login: str, ip_addr: str):
    data = []

    if not os.path.isfile('logs.json'):
        with open('logs.json', 'w+') as file_writer:
            json.dump(data, file_writer)
    else:
        with open('logs.json', 'r') as file_reader:
            data = json.load(file_reader)

    data.append({
        'date': str(datetime.now()),
        'protocol': protocol,
        'login': _login,
        'ip_addr': ip_addr
    })
    # data.append({
    #     'date': str(datetime.now()),
    #     'protocol': protocol,
    #     'login': "clara.rabouan@gmail.com",
    #     'ip_addr': "173.194.76.109"
    # })

    with open('logs.json', 'w') as file_writer:
        json.dump(data, file_writer, indent=4)


def login():
    _user_address = None
    _imap_connection = None
    _smtp_connection = None

    while True:
        print(" --- Login --- ")
        _user_address = None
        while True:
            _user_address = input("E-mail: ")
            if re.match(r"([^.@]+)(\.[^.@]+)*@([^.@]+\.)+([^.@]+)", _user_address):
                break
            else:
                print("Wrong format of mail")
        password = getpass("Password: ")  # input("Password: ")
        mail_server = _user_address.split('@')[1].split('.')[0]
        imap_addr = IMAP_DICT.get(mail_server, "No imap server address associated.")
        smtp_addr = SMTP_DICT.get(mail_server, "No smtp server address associated.")
        if not (isinstance(imap_addr, tuple) and isinstance(smtp_addr, tuple)):
            print("This email address isn't supported.")
            continue

        _imap_connection = imaplib.IMAP4_SSL(imap_addr[0])
        try:
            _imap_connection.login(_user_address, password)

            imap_socket = _imap_connection.socket()
            # print(str(imap_socket))
            ip_addr = str(imap_socket).split('raddr')[1].replace('>', '').replace('=', '').split("'")[1]
            # <ssl.SSLSocket fd=968, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM,
            # proto=0, laddr=('192.168.0.46', 3581), raddr=('64.233.184.109', 993)>
            log_connection('imap', _user_address, ip_addr)

        except _imap_connection.error as e:
            if 'Invalid credentials' in str(e):
                print('IMAP Invalid credentials')
            else:
                print('IMAP Error')
            continue

        _smtp_connection = smtplib.SMTP(smtp_addr[0], smtp_addr[1])
        _smtp_connection.ehlo()
        _smtp_connection.starttls()
        _smtp_connection.ehlo()
        try:
            _smtp_connection.login(_user_address, password)

            smtp_socket = _smtp_connection.sock
            # print(str(smtp_socket))
            ip_addr = str(smtp_socket).split('raddr')[1].replace('>', '').replace('=', '').split("'")[1]
            log_connection('smtp', _user_address, ip_addr)
        except smtplib.SMTPAuthenticationError:
            print('SMTP Invalid credentials')
            continue

        break

    sqlite_db = sqlite3.connect('mails.db')
    c = sqlite_db.cursor()
    # Adding the email account to the database if it isn't in it already
    response = list(c.execute("SELECT COUNT(*) FROM accounts WHERE account_address = '" + _user_address + "'"))
    if len(response) > 0 and int(response[0][0]) == 0:
        c.execute("INSERT INTO accounts VALUES ('" + _user_address + "')")
    sqlite_db.commit()
    sqlite_db.close()

    return _user_address, _imap_connection, _smtp_connection


def logout():
    imap_connection.close()
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
    mail_ids = {
        "inbox": [],
        "sent": []
    }

    sqlite_db = sqlite3.connect('mails.db')
    c = sqlite_db.cursor()

    # Mail Inbox
    imap_connection.select()  # "inbox"
    status, data = imap_connection.search(None, 'ALL')
    for block in data:
        mail_ids["inbox"] += block.split()

    # Mail sent
    # for _i in imap_connection.list()[1]:
    #     l = _i.decode().split(' "/" ')
    #     if "sent" in l[0].lower():
    #         sent_box = l[1]
    # imap_connection.select(sent_box)
    # status, data = imap_connection.search(None, 'ALL')
    # for block in data:
    #     mail_ids["sent"] += block.split()

    for box in mail_ids:
        for _i in mail_ids[box]:
            status, data = imap_connection.fetch(_i, '(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    message = email.message_from_bytes(response_part[1])

                    # print('Mail number ' + str(i))
                    # for key in message:
                    #     print(key)
                    # print("#############################################")

                    mail_id = message['message-id']

                    id_count = list(c.execute("SELECT COUNT(*) FROM mails WHERE mail_id = '" + mail_id + "'"))
                    if len(id_count) > 0 and int(id_count[0][0]) == 0:
                        # print(mail_id)
                        mail_from = str(email.header.make_header(email.header.decode_header(message['from'])))
                        mail_to = str(email.header.make_header(email.header.decode_header(message['to'])))
                        mail_subject = str(email.header.make_header(email.header.decode_header(message['subject'])))
                        mail_date = str(message['date'])

                        if message.is_multipart():
                            mail_content = ''

                            for part in message.get_payload():
                                if part.get_content_type() == 'text/plain':
                                    mail_content += part.get_payload()
                        else:
                            mail_content = message.get_payload()

                        mail_attachments = ''
                        mail_is_outbound = box == 'sent'


                        # print("INSERT INTO mails VALUES ('" +
                        #       mail_id + "','" +
                        #       mail_from + "','" +
                        #       mail_to + "','" +
                        #       sql_escape(mail_subject) + "','" +
                        #       sql_escape(mail_content) + "','" +
                        #       mail_attachments + "','" +
                        #       mail_date + "'," +
                        #       str(int(mail_is_outbound)) + ',"' +
                        #       user_address + '")')
                        c.execute("INSERT INTO mails VALUES ('" +
                                  mail_id + "','" +
                                  mail_from + "','" +
                                  mail_to + "','" +
                                  sql_escape(mail_subject) + "','" +
                                  sql_escape(mail_content) + "','" +
                                  mail_attachments + "','" +
                                  mail_date + "'," +
                                  str(int(mail_is_outbound)) + ',"' +
                                  user_address + '")')

    sqlite_db.commit()
    sqlite_db.close()


def read():
    request = 'SELECT * FROM mails where mail_is_outbound=0'
    verif = "Error"

    conn = sqlite3.connect('mails.db')
    c = conn.cursor()

    # while request == "Error":
    #     case = int(input("Read:\n1:Mail sent\n2:Mail received\n"))
    #     switch = {
    #         1: 'SELECT * FROM mails where mail_is_outbound=1',
    #         2: 'SELECT * FROM mails where mail_is_outbound=0'
    #     }
    #     request = str(switch.get(case, "Error"))

    while verif == "Error":
        case = int(input("Choose to sort by:\n1: Date\n2: Mail from\n3: Mail to\n4: Subject\n"))
        switch = {
            1: ('Date', ' ORDER BY mail_date DESC;'),
            2: ('From', ' ORDER BY mail_from;'),
            3: ('To', ' ORDER BY mail_to_list;'),
            4: ('Subject', ' ORDER BY mail_subject;')
        }
        verif = str(switch.get(case, "Error"))
    request += str(switch.get(case)[1])

    cpt = 1
    if list(c.execute('SELECT COUNT(*) FROM mails'))[0][0] == 0:
        print("There are no mails in the inbox!")
        return

    clear()
    print("E-mails in the inbox sorted by " + switch.get(case, "Error")[0])

    for row in c.execute(request):
        print("--------------------------------------------\n" +
              str(cpt) + ") From: " + row[1] + "\n" +
              "Subject: "+row[3])
        cpt += 1

    while True:
        email_selected = int(input("\nChoose the number of the email to read: "))
        if 0 < email_selected <= cpt-1:
            break

    row = c.execute(request).fetchall()
    print("--------------------------------------------\n" +
          "From: " + row[email_selected-1][1] + "\n" +
          "To: " + row[email_selected-1][2] + "\n" +
          "Subject: " + row[email_selected-1][3] + "\n" +
          " --- Content --- \n" +
          row[email_selected-1][4] + "\n")
    conn.close()

    choice = input("Would you like to save the email? [y/n] ")
    if choice == "y":
        # num = input("Number of the email to save? ")
        savetofile(request, str(email_selected))


def savetofile(request, num: str):
    filename = input("\nChoose the name the file: ")+".eml"
    cpt = 1
    conn = sqlite3.connect('mails.db')
    c = conn.cursor()
    for row in c.execute(request):
        if num == str(cpt):
            f = open(filename, 'w')
            f.write("To: " + row[1] +
                    "\nSubject: " + row[3] +
                    "\nFrom: " + row[2] +
                    "\nMessage-ID: " + row[0] +
                    "\nDate: " + row[6] +
                    "\nContent-Type: text/plain; charset=utf-8" +
                    "\nContent-Transfer-Encoding: quoted-printable\n" +
                    "\n" + row[4] +
                    "\nAttachment: " + row[5])
            f.close()
            print("The mail has been saved in: "+filename)
        cpt += 1
    conn.close()
    return


def delete():
    choice = 0
    while choice <= 0 or choice > 2:
        print("Where would you like to delete the e-mails?\n" +
              "1: In the inbox of the mail server\n" +
              "2: In the sqlite database (all the mails)")
        try:
            choice = int(input())
        except ValueError:
            print("Error: The given answer is not a number.")
            continue
        if choice <= 0 or choice > 2:
            print("Error: This number is not assigned")

    if choice == 1:
        choice_2 = 0
        while choice_2 <= 0 or choice_2 > 2:
            print("How would you like to delete e-mails?\n" +
                  "1: One mail at a time\n" +
                  "2: All mails")
            try:
                choice_2 = int(input())
            except ValueError:
                print("Error: The given answer is not a number.")
                continue
            if choice_2 <= 0 or choice_2 > 2:
                print("Error: This number is not assigned")

        if choice_2 == 1:
            imap_connection.select()
            status, data = imap_connection.search(None, 'ALL')
            for block in data[0].split():
                block_status, block_data = imap_connection.fetch(block, '(RFC822)')
                for response_part in block_data:
                    if isinstance(response_part, tuple):
                        message = email.message_from_bytes(response_part[1])
                        mail_from = str(email.header.make_header(email.header.decode_header(message['from'])))
                        mail_to = str(email.header.make_header(email.header.decode_header(message['to'])))
                        mail_subject = str(email.header.make_header(email.header.decode_header(message['subject'])))
                        mail_date = str(message['date'])
                        print("From: " + mail_from +
                              "; To: " + mail_to +
                              "; Subject: " + mail_subject +
                              "; Date: " + mail_date)
                        choice_3 = input("Delete this mail? [y/n] [any other input to stop] ")
                        if choice_3.lower() == "y":
                            imap_connection.store(block, '+FLAGS', '\\Deleted')
                        elif choice_3.lower() == "n":
                            continue
                        else:
                            break

            imap_connection.expunge()
            print("Inbox expunged.")

        if choice_2 == 2:
            if input("Are you sure? All emails will be deleted. [y/n] ") == "y":
                imap_connection.select()
                status, data = imap_connection.search(None, 'ALL')
                for block in data[0].split():
                    imap_connection.store(block, '+FLAGS', '\\Deleted')
                imap_connection.expunge()
                print("Inbox expunged.")
        else:
            print("This number is not assigned")

    elif choice == 2:
        conn = sqlite3.connect('mails.db')
        c = conn.cursor()
        c.execute('''DROP TABLE IF EXISTS mails''')
        conn.close()
        db_init()
        print("Table dropped.")


def send():
    response = "n"
    to = None
    subject = None
    content = None
    attachment = None
    path = None

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
        print("--------------------------------------------\n" +
              "From: " + user_address + "\n" +
              "To: " + to + "\n" +
              "Subject: " + subject + "\n" +
              " --- Content --- \n" +
              content + "\n" +
              "--------------------------------------------\n")
        attachment = input("Would you like to add an attachment? [y/n] ")
        if attachment == "y":
            path = input(
                "Enter the path and the name of the file to attach or just the name if you are in the same directory: ")
        response = input("Send the e-mail? [y/n] ")
    msg = MIMEMultipart()
    msg['From'] = user_address
    msg['To'] = to
    msg['Subject'] = subject
    message = content
    msg.attach(MIMEText(message))

    if attachment == "y":
        # attach_file_name = 'C:/Users/thibault/Desktop/Advanced structure/ADSA mini project/server_project_mail/attachment.txt'
        attach_file = open(path, 'rb')  # Open the file as binary mode
        payload = MIMEBase('application', 'octate-stream')
        payload.set_payload(attach_file.read())
        encoders.encode_base64(payload)  # encode the attachment
        # add payload header with filename
        payload.add_header('Content-Decomposition', 'attachment', filename=path)
        msg.attach(payload)
    smtp_connection.sendmail(user_address, to, msg.as_string())
    print("Mail send successfully!!\n")


def sql_escape(statement: str):
    statement = statement.replace('\\', '\\\\')
    for char in SQL_ESCAPE_DICT:
        statement = statement.replace(char, SQL_ESCAPE_DICT[char])
    return statement


def menu(case: int):
    switch = {
        1: retrieve,
        2: send,
        3: read,
        4: delete,
        5: logout
    }
    func = switch.get(case, lambda: print("Error : The given answer is not in the list."))
    func()


if __name__ == '__main__':
    while True:
        clear()
        db_init()
        user_address, imap_connection, smtp_connection = login()
        retrieve()

        print("Menu:")

        entry_names = ["Refresh database", "Send", "Read", "Delete", "Logout"]

        entry_number = -1
        while True:
            if entry_number == 5:
                logout()
                break
            for i in range(len(entry_names)):
                print(str(i + 1) + ": " + entry_names[i])

            try:
                entry_number = int(input("Desired menu entry number: "))

                menu(entry_number)
            except ValueError:
                print("Error: The given answer is not a number.")
