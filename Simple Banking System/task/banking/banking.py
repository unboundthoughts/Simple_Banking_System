# Write your code here
import random
import sys
import sqlite3

conn = sqlite3.connect('card.s3db')

cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS card
(
    id INTEGER
    , number TEXT
    , pin TEXT
    , balance INTEGER DEFAULT 0
)
''')  # check if table exists if not then create table
conn.commit()

account_dict = {}
# global in_card, in_pin
in_card = in_pin = ''


def fn_main_menu():
    print('''
    1. Create an account
    2. Log into account
    0. Exit 
    ''')

    return input('\n>')


def fn_luhn(credit_card_number):  # 15 digit required
    l_cc = list(credit_card_number)
    i_l_cc = []
    tot = 0
    # print(len(l_cc))
    for i in range(len(l_cc)):  # -1 to drop the last digit. if it was the test checksum
        i_l_cc.append(int(l_cc[i]))

        if (i + 1) % 2 != 0:  # odd
            i_l_cc[i] *= 2

        if i_l_cc[i] > 9:
            i_l_cc[i] -= 9

        tot += i_l_cc[i]
        # print(l_cc[i], i_l_cc[i], tot)

    tot_next_10 = tot
    if tot_next_10 % 10:
        tot_next_10 = tot_next_10 + (10 - tot_next_10 % 10)

    checksum = tot_next_10 - tot
    # print(checksum)
    return str(checksum)


def create_account():
    iin = '400000'
    # customer_account_number = '493832089'
    customer_account_number = str(random.randint(100000000, 999999999))
    checksum = fn_luhn(iin + customer_account_number)
    card_no = iin + customer_account_number + checksum
    # pin = '6826'
    pin = str(random.randint(1000, 9999))

    # Store card info in db
    cur.execute('select ifnull(max(id),0) from card')
    next_id = cur.fetchone()[0] + 1
    print(next_id)
    cur.execute('''
    insert into card (id, number,pin)
    values (?, ?, ?)
    ''', (next_id, card_no, pin))
    conn.commit()

    # store the card_no and pin
    global account_dict
    # account_dict = dict.fromkeys({card_no}, pin)
    new_account_dict = {card_no: pin}
    account_dict.update(new_account_dict)
    # print(account_dict)
    print('''

Your card has been created
Your card number:
{}
Your card PIN:
{}
    '''.format(card_no, str(pin)))

    conn.commit()


def fn_login():
    global in_card, in_pin
    print('Enter your card number:')
    in_card = input('>')
    print('Enter your PIN:')
    in_pin = input('>')

    # fetch card info
    cur.execute('''
    select number, pin 
    from card
    where number = ?
        and pin = ? 
    ''', (in_card, in_pin))

    row = cur.fetchone()
    # print("Info ", row, type(row), cur.rowcount)
    # for row in cur:
    if row is not None:
        number_db = row[0] if type(row[0]) != "None" else "N/A"
        pin_db = row[1] if type(row[1]) != "None" else "N/A"
        # print(number_db, pin_db)

        if number_db != in_card \
                or pin_db != in_pin:
            print('Wrong card number or PIN!')
            return False
        elif number_db == in_card \
                or pin_db == in_pin:
            print('You have successfully logged in!')
            return True
        else:
            print('Something wrong!')
    else:
        print('Wrong card number or PIN!')
        return False

    # print(account_dict.get(in_card))
    # if str(account_dict.get(in_card)) == 'None' \
    #         or str(account_dict.get(in_card)) != in_pin:
    #     print('Wrong card number or PIN!')
    #     return False
    # elif str(account_dict.get(in_card)) == in_pin:
    #     print('You have successfully logged in!')
    #     return True
    # else:
    #     print('Something wrong!')


def exit_program():
    print('\nBye!')
    sys.exit()


def fn_in_menu():
    print('''
    1. Balance
    2. Add income
    3. Do transfer
    4. Close account
    5. Log out
    0. Exit
    ''')
    return input('>')


def fn_add_income():
    income = input("Enter income: ")
    cur.execute('''
    update card
    set balance = balance + ?
    where number = ?
        and pin = ?
    ''', (income, in_card, in_pin))
    conn.commit()
    print('Income was added!')


def fn_display_balance():
    cur.execute('''select balance
    from card
    where number = ?
        and pin = ?
    ''', (in_card, in_pin))
    balance = cur.fetchone()[0]
    print('Balance: {}'.format(balance))


def fn_transfer_money():
    print('Enter card number:')
    tr_number = input('>')
    # print(tr_number[:-1], " -> ", tr_number[-1])
    tr_checksum = fn_luhn(tr_number[:-1])
    # print(tr_checksum)
    if tr_number[-1] != tr_checksum:
        print('Probably you made a mistake in the card number. Please try again')
    elif tr_number == in_card:
        print("You can't transfer money to the same account!")
    else:
        # check if card exists
        # print(tr_number)
        cur.execute('''
        select number 
        from card
        where number = ?
        ''', (tr_number,))
        row = cur.fetchone()
        # print(bal) # e.g. (1690,)
        # print(bal[0], type(bal)) # e.g. 1690 <class 'tuple'>
        if row is not None:
            # card exists so transfer
            print('Enter how much money you want to transfer:')
            tr_amount = int(input('>'))

            cur.execute('''
            select balance 
            from card 
            where number = ?
            ''', (in_card,))
            current_bal_from = int(cur.fetchone()[0])
            print(current_bal_from)

            if tr_amount > current_bal_from:
                print("Not enough money!")
            else:
                cur.execute('''
                update card
                set balance = balance + ?
                where number = ?
               ''', (tr_amount, tr_number))
                conn.commit()

                cur.execute('''
                update card
                set balance = balance - ?
                where number = ?
               ''', (tr_amount, in_card))
                conn.commit()

                print("Success!")
                # row = cur.fetchone()
        else:
            print('Such a card does not exist.')


def fn_close_account():
    conn.execute('''
    delete from card
    where number = ?
    ''', (in_card,))
    conn.commit()
    print('The account has been closed!')


while True:
    mm_sel = fn_main_menu()
    if mm_sel == '1':
        create_account()
    elif mm_sel == '2':
        print(account_dict)
        if fn_login():
            while True:
                login_sel = fn_in_menu()
                if login_sel == '1':
                    # print('\nBalance: {}'.format('0'))
                    fn_display_balance()
                if login_sel == '2':
                    # print('\nAdd income: {}'.format('0'))
                    fn_add_income()
                if login_sel == '3':
                    print('Transfer')
                    fn_transfer_money()
                if login_sel == '4':
                    fn_close_account()
                    break
                elif login_sel == '5':
                    print('\nYou have successfully logged out!')
                    break
                elif login_sel == '0':
                    exit_program()
    elif mm_sel == '0':
        exit_program()
conn.commit
conn.close()
