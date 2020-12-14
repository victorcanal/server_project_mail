import sqlite3


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


def function_one():
    return " --- Executing function_one"


def function_two():
    return " --- Executing function_two"


def function_three():
    return " --- Executing function_three"


def menu(case: int):
    switch = {
        1: function_one,
        2: function_two,
        3: function_three
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
        except ValueError:
            print("Error : The given answer is not a number.")
            break
        if entry_number > len(entry_names) or entry_number <= 0:
            print("Error : The given answer is not in the list.")
            break

    print("You selected menu entry number " + str(entry_number) + " : " + str(entry_names[entry_number - 1]))
    menu(entry_number)
