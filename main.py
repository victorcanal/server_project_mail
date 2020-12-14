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

    # connect to the server and go to its inbox
    mail = imaplib.IMAP4_SSL(SERVER)
    mail.login(EMAIL, PASSWORD)
    # we choose the inbox but you can select others
    mail.select('inbox')

    # we'll search using the ALL criteria to retrieve
    # every message inside the inbox
    # it will return with its status and a list of ids
    status, data = mail.search(None, 'ALL')
    # the list returned is a list of bytes separated
    # by white spaces on this format: [b'1 2 3', b'4 5 6']
    # so, to separate it first we create an empty list
    mail_ids = []
    # then we go through the list splitting its blocks
    # of bytes and appending to the mail_ids list
    for block in data:
        # the split function called without parameter
        # transforms the text or bytes into a list using
        # as separator the white spaces:
        # b'1 2 3'.split() => [b'1', b'2', b'3']
        mail_ids += block.split()

    # now for every id we'll fetch the email
    # to extract its content
    for i in mail_ids:
        # the fetch function fetch the email given its id
        # and format that you want the message to be
        status, data = mail.fetch(i, '(RFC822)')

        # the content data at the '(RFC822)' format comes on
        # a list with a tuple with header, content, and the closing
        # byte b')'
        for response_part in data:
            # so if its a tuple...
            if isinstance(response_part, tuple):
                # we go for the content at its second element
                # skipping the header at the first and the closing
                # at the third
                message = email.message_from_bytes(response_part[1])

                # with the content we can extract the info about
                # who sent the message and its subject
                mail_from = message['from']
                mail_to = message['to']
                mail_subject = message['subject']
                mail_date = str(datetime.datetime.now())
                print(mail_date)
                #mail_date = sqlite3.datetime.

                # then for the text we have a little more work to do
                # because it can be in plain text or multipart
                # if its not plain text we need to separate the message
                # from its annexes to get the text
                if message.is_multipart():
                    mail_content = ''

                    # on multipart we have the text message and
                    # another things like annex, and html version
                    # of the message, in that case we loop through
                    # the email payload
                    for part in message.get_payload():
                        # if the content type is text/plain
                        # we extract it
                        if part.get_content_type() == 'text/plain':
                            mail_content += part.get_payload()
                else:
                    # if the message isn't multipart, just extract it
                    mail_content = message.get_payload()

                # and then let's show its result
                #print(f'From: {mail_from}')
                #print(f'Subject: {mail_subject}')
                #print(f'Content: {mail_content}')
                conn = sqlite3.connect('mail.db')
                c = conn.cursor()
                c.execute(f"INSERT INTO mail VALUES ('{mail_from}','{mail_to}','{mail_subject}','mail_date',' '")
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
    func = switch.get(case, lambda: "Switcher error")
    func()


if __name__ == '__main__':
    print("Menu :")
    entry_names = ["entry 1", "entry 2", "entry 3"]

    for i in range(len(entry_names)):
        print("Entry " + str(i + 1) + " : " + entry_names[i])

    entry_number = -1
    while True:
        try:
            print("Desired menu entry number: ")
            entry_number = int(input())
            break
        except ValueError:
            print("Error : The given answer is not a number.")
        if entry_number > len(entry_names) or entry_number <= 0:
            print("Error : The given answer is not in the list.")

    print("You selected menu entry number " + str(entry_number) + " : " + str(entry_names[entry_number - 1]))
    menu(entry_number)
