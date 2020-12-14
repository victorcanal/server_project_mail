import sqlite3;

def connect():
    conn = sqlite3.connect('mail.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE mail
                 (source text, destination text, data text, date datetime, text filepath)''')
    c.execute("INSERT INTO mail VALUES ('Dupont','Moi','Bonjour','2020-12-14 20:22:30.500','')")
    conn.commit()
    conn.close()

def read():
    conn = sqlite3.connect('mail.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM mail ORDER BY source'):
        print(row)
    conn.close()

def send(file):
    return


if __name__ == '__main__':
    #connect()
    read()
