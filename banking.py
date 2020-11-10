# https://hyperskill.org/projects/109/stages/594/implement
import random
import sys
import sqlite3
from functools import reduce


def luhn(code):
    # from wiki
    # Предварительно рассчитанные результаты умножения на 2 с вычетом 9 для больших цифр
    # Номер индекса равен числу, над которым проводится операция
    LOOKUP = (0, 2, 4, 6, 8, 1, 3, 5, 7, 9)
    code = reduce(str.__add__, filter(str.isdigit, code))
    evens = sum(int(i) for i in code[-1::-2])
    odds = sum(LOOKUP[int(i)] for i in code[-2::-2])
    return (evens + odds) % 10 == 0


class BankingSystem:

    # dict_with_pins = {}
    id = 1

    def __init__(self):
        pass

    def show_main_menu(self):
        PROMPT = ('''1. Create an account
2. Log into account
0. Exit\n''')
        while True:
            print(PROMPT)
            action = input()
            if action == '1':
                BankingSystem.create_account(self)
            elif action == '2':
                BankingSystem.login(self)
            elif action == '0':
                print('Bye!')
                sys.exit(0)

    def show_logged_in_menu(self, card_number):
        PROMPT = '''1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit\n'''
        while True:
            print(PROMPT)
            action = input()
            if action == '1':
                self.show_balance(self, card_number)
            elif action == '2':
                pass  # add income
                self.add_income(self, card_number)
            elif action == '3':
                pass  # do transfer
                self.transfer_money(self, card_number)
            elif action == '4':
                pass  # close account
                self.delete_account(self, card_number)
            elif action == '5':
                print('You have successfully logged out!\n')
                self.show_main_menu()
            elif action == '0':
                print('Bye!')
                sys.exit(0)

    def create_account(self):
        random.seed()
        card_number = '400000'
        for _ in range(9):
            card_number += str(random.randint(0, 9))

        # luhn algorithm
        card_number_luhn = []
        for i in range(15):
            number = int(card_number[i])
            if i in [0, 2, 4, 6, 8, 10, 12, 14]:
                number *= 2
            if number > 9:
                number -= 9
            card_number_luhn.append(number)

        # find checksum (last_digit)
        last_number = 0
        while (sum(card_number_luhn) + last_number) % 10 != 0:
            last_number += 1

        card_number += str(last_number)
        pin_number = ''
        for _ in range(4):
            pin_number += str(random.randint(0, 9))
        print('Your card has been created')
        print('Your card number:')
        print(card_number)
        print('Your card PIN:')
        print(pin_number)
        cur.execute('''INSERT INTO card (id, number, pin, balance) VALUES (?, ?, ?, 0);''',
                    (BankingSystem.id, card_number, pin_number))
        BankingSystem.id += 1
        conn.commit()

    def login(self):
        card_number = input('Enter your card number:\n')
        pin_number = input('Enter your PIN:\n')
        cur.execute('''SELECT number FROM card WHERE number = ?;''', (card_number,))
        # if no such card number -> WRONG
        if not cur.fetchone():
            print('Wrong card number or PIN!\n')
        else:
            cur.execute('''SELECT pin FROM card WHERE number = ?;''', (card_number,))
            if cur.fetchone()[0] == pin_number:
                print('You have successfully logged in!\n')
                self.show_logged_in_menu(self, card_number)
            else:
                print('Wrong card number or PIN!\n')

    def show_balance(self, card_number):
        cur.execute('''SELECT balance FROM card WHERE number = ?;''', (card_number,))
        print('Balance: ', cur.fetchone()[0])

    def add_income(self, card_number):
        print('Enter income:\n')
        add_to_balance = int(input())
        cur.execute('''UPDATE card SET balance = balance + ? WHERE number = ?;''', (add_to_balance, card_number,))
        conn.commit()
        print('Income was added!\n')

    def transfer_money(self, card_number):
        send_to_card = input('Transfer\nEnter card number:')
        cur.execute('''SELECT number FROM card WHERE number = ?;''', (send_to_card,))
        # check card number with luhn algo
        if not luhn(send_to_card):
            print('Probably you made a mistake in the card number. Please try again!\n')
        # no such card
        elif not cur.fetchone():
            print('Such a card does not exist.\n')
        # card number correct
        else:
            send_how_much = int(input('Enter how much money you want to transfer:\n'))
            cur.execute('''SELECT balance FROM card WHERE number = ?;''', (card_number,))
            if cur.fetchone()[0] < send_how_much:
                print('Not enough money!\n')
            else:
                cur.execute('''UPDATE card SET balance = balance - ? WHERE number = ?;''', (send_how_much, card_number,))
                conn.commit()
                cur.execute('''UPDATE card SET balance = balance + ? WHERE number = ?;''', (send_how_much, send_to_card,))
                conn.commit()
                print('Success!\n')

    def delete_account(self, card_number):
        cur.execute('''DELETE FROM card WHERE number = ?;''', (card_number,))
        conn.commit()
        print('The account has been closed!\n')


# Executes some SQL query
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

# cur.execute('CREATE DATABASE card.s3db;')
cur.execute('CREATE TABLE if NOT EXISTS card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')
conn.commit()

my_banking_system = BankingSystem
BankingSystem.show_main_menu(my_banking_system)
conn.close()
