import random
import sqlite3

number_of_card = 0
MENU_PROMPT = """1. Create an account
2. Log into account
0. Exit
"""

MENU_PROMPT_LOGGED = """1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
"""
CREATE_CARD_TABLE = "CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER " \
                    "DEFAULT 0); "

INSERT_CARD = "INSERT INTO card (number, pin) VALUES (?, ?);"

GET_ALL_CARD = "SELECT * FROM card;"

GET_CARD_BY_NUMBER = "SELECT * FROM card WHERE number = ?;"

GET_ALL_RECORDS = "SELECT * FROM card;"

CHECK_NUMBER = "SELECT number FROM card WHERE number = ?;"

DELETE_ACCOUNT = "DELETE FROM card WHERE number = ?;"

CHANGE_BALANCE = "UPDATE card SET balance = ? WHERE number = ?;"


def connect():
    return sqlite3.connect("card.s3db")


def create_table(connection):
    with connection:
        connection.execute(CREATE_CARD_TABLE)


def add_card(connection, number, pin):
    with connection:
        connection.execute(INSERT_CARD, (number, pin))


def get_card_by_number(connection, number):
    with connection:
        return connection.execute(GET_CARD_BY_NUMBER, (number,)).fetchall()


def delete_acc(connection, number):
    with connection:
        return connection.execute(DELETE_ACCOUNT, (number,))


def change_balance(connection, amount, number):
    with connection:
        return connection.execute(CHANGE_BALANCE, (amount, number))


conn = connect()


def menu():
    global conn
    create_table(conn)

    while (user_input := input(MENU_PROMPT)) != '':
        if user_input == '1':
            acc_create()
        elif user_input == '2':
            login(input('Enter your card number:\n'), input('Enter your PIN:\n'))
        elif user_input == '0':
            exit_()


def menu_logged():
    while (user_input := input(MENU_PROMPT_LOGGED)) != '':
        if user_input == '1':
            balance(conn, number_of_card)
        elif user_input == '2':
            income_add()
        elif user_input == '3':
            do_transfer()
        elif user_input == '4':
            close_acc()
        elif user_input == '5':
            log_out()
        elif user_input == '0':
            exit_()


def luhn_checksum(card_number):
    def digits_of(n):
        return [int(_) for _ in str(n)]

    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10


def is_luhn_valid(card_number):
    return luhn_checksum(card_number) == 0


# system methods
def acc_create():
    bank_id = '400000'
    card_num = bank_id + ''.join([str(random.randint(0, 9)) for _ in range(9)])
    pin = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    global conn

    card_num = card_num + str(luhn_checksum(card_num))

    card_valid = is_luhn_valid(card_num)

    checking_valid = get_card_by_number(conn, card_num)
    if card_num not in checking_valid and card_valid is True:
        add_card(conn, card_num, pin)
        print('Your card has been created\nYour card number:\n'
              f'{card_num}\nYour card PIN:\n{pin}')
    else:
        acc_create()


def login(card_number, pin):
    global number_of_card
    check_card = get_card_by_number(conn, card_number)
    if check_card:
        if check_card[0][1] and check_card[0][2] == pin:
            print('\nYou have successfully logged in!\n')
            number_of_card = card_number
            menu_logged()
        else:
            print('\nWrong card number or PIN!\n')
            menu()
    else:
        print('\nWrong card number or PIN!\n')
        menu()


def exit_():
    print('Bye!\n')
    conn.close()
    exit()


def log_out():
    print('\nYou have successfully logged out!\n')
    menu()


def balance(connection, card_number):
    print(f'\nBalance: {get_card_by_number(connection, card_number)[0][3]}\n')


def income_add():
    income = input('Enter income: \n')
    change_balance(conn, get_card_by_number(conn, number_of_card)[0][3] + int(income), number_of_card)
    print('Income was added!\n')
    menu_logged()


def do_transfer():
    transfer_card_num = input('Enter card number:\n')
    if is_luhn_valid(transfer_card_num) is False:
        print('Probably you made a mistake in the card number. Please try again!\n')
        menu_logged()
    elif not get_card_by_number(conn, transfer_card_num):
        print('Such a card does not exist.\n')
        menu_logged()
    elif transfer_card_num == number_of_card:
        print("You can't transfer money to the same account!\n")
        menu_logged()
    else:
        def transfer_work():
            transfer_amount = input('Enter how much money you want to transfer:\n')
            if int(transfer_amount) > int(get_card_by_number(conn, number_of_card)[0][3]):
                print('Not enough money!\n')
                menu_logged()
            else:
                change_balance(conn, get_card_by_number(conn, number_of_card)[0][3] - int(transfer_amount),
                               number_of_card)

                change_balance(conn, get_card_by_number(conn, transfer_card_num)[0][3] + int(transfer_amount),
                               transfer_card_num)
                print('Success!\n')
                menu_logged()

        transfer_work()


def close_acc():
    delete_acc(conn, number_of_card)
    print('\nThe account has been closed!\n')
    menu()


menu()
