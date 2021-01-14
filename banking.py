import random
import sqlite3
import string
from sys import exit
#Establish SQL connection
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

#DELETE IF ANYTHING IN DB
cur.execute("DELETE FROM card;")
conn.commit()

## Create CARD table in DB
cur.execute('''CREATE TABLE IF NOT EXISTS card (
            id INTEGER,
            number TEXT,
            pin TEXT,
            balance INTEGER DEFAULT 0)
''');
conn.commit()

#prints main menu
def printMenu():
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")

#prints menu after logging in
def printLogMenu():
    print('1. Balance')
    print('2. Add income')
    print('3. Do transfer')
    print('4. Close account')
    print('5. Log out')
    print('0. Exit')

def store(pdict, username, password):
    pdict[username] = password

#verifies number using luhnAlgo
def luhnAlgo(cardnumber):
  global checksum
  cardnumber2 =list(cardnumber)
  for index in range(0,len(cardnumber),2):
    cardnumber2[index] = str(int(cardnumber[index])*2)
    if int(cardnumber2[index]) > 9:
      cardnumber2[index]=int(cardnumber2[index])-9
    else:
      pass
  total =0
  for item in range(0, len(cardnumber2)):
    total = total + int(cardnumber2[item])
  mod10=total%10
  checksum = 10-mod10
  if checksum == 10:
      checksum=0
  else:
    pass

def luhnAlgo_check(cardnumber):
    global checksum_cn, checksum
    cardnumber_nochecksum=list(cardnumber)
    cardnumber_nochecksum.pop()
    cardnumber_nochecksum=''.join(cardnumber_nochecksum)
    print(cardnumber_nochecksum)
    luhnAlgo(cardnumber_nochecksum)
    #get last digit of cardnumber
    checksum_cn=cardnumber[len(cardnumber)-1]

def checkDB(cardnumber,pin):
    global checked,conn,curr
    checked=False
    cur.execute("SELECT * FROM card;")
    row = cur.fetchall()
    for i in row:
        cond1 = i[1]==card_num
        cond2 = i[2]==pin
        if cond1==True and cond2 == True:
            checked = True
        else:
            pass
    if checked==True:
        print('successfully logged in')
    else:
        print('Wrong card number or PIN!')

def checkDB_transfer(cardnumber):
    global checked2,conn,curr
    checked2=False
    cur.execute("SELECT * FROM card;")
    row = cur.fetchall()
    for i in row:
        cond1 = i[1]==cardnumber
        if cond1==True:
            checked2 = True
            break
        else:
            checked2=False
    if checked2==True:
        pass
    else:
        print("Such a card does not exist.")

#could combine the get_balance and show_balance
def get_balance(cardnumber):
    global conn,curr
    global new_bal
    cur.execute("SELECT * FROM card;")
    row = cur.fetchall()
    for i in row:
        cond1 = i[1]==cardnumber
        if cond1==True:
            checked = True
            new_bal=i[3]
        else:
            pass

def show_balance(cardnumber):
    global conn,curr
    cur.execute("SELECT * FROM card;")
    row = cur.fetchall()
    for i in row:
        cond1 = i[1]==card_num
        if cond1==True:
            checked = True
            print('balance is '+str(i[3]))
        else:
            pass

#this is later and the code just double check before deleting
UPDATE_BAL_SQL='''UPDATE card
SET balance = ?
WHERE number = ?;'''

x=1
id=0
database = {}
m2inp=None
while x != 0:
    if m2inp==0:
        break
    else:
        printMenu()
        choice = input()

        if choice == '1':
                BIN = '400000'
                s = ""
                for i in range(9):
                  n = random.randint(0,9)
                  s+=str(n)
                pre_card_num = BIN + s

                checksum = ''
                # LUHN ALGO
                luhnAlgo(pre_card_num)
                card_num = BIN + s + str(checksum)

                #creating pin
                p =''
                for i in range(4):
                  n = random.randint(0,9)
                  p+=str(n)
                pin = p

                # Print the information
                print("Your card number:")
                print(card_num)
                print("Your card PIN:")
                print(pin)

                id +=1
                ## save to db as new card entry
                cur.execute('''INSERT INTO card (id,number,pin) VALUES(?,?,?);''',(id,card_num,pin))
                conn.commit()


        elif choice == '2':
            print("Enter your card number:")
            card_num = input()
            cn=str(card_num)
            print("Enter your pin")
            pin = input()

            checkDB(card_num,pin)
            while checked == True:
                printLogMenu()
                m2inp=int(input())

                #1-'BALANCE'
                if m2inp == 1:
                    show_balance(card_num)

                #2-'ADD INCOME'
                elif m2inp == 2:
                    #amount to add based on user input
                    print('How much would you like to add?')
                    balance_AmountAdd = int(input())
                    new_bal=0
                    get_balance(card_num)
                    #OG VALUE AKA --> the balance currently --> cardnum
                    balance_TotalBal = balance_AmountAdd + new_bal
                    #update card value
                    UPDATE_BAL_SQL='''UPDATE card SET balance = ? WHERE number = ?'''
                    cur.execute(UPDATE_BAL_SQL,(balance_TotalBal,card_num))
                    conn.commit()
                    #print balance
                    show_balance(card_num)

                #3-'DO TRANSFER'
                elif m2inp == 3:
                    print('Transfer')
                    print('Enter card number:')
                    trans_cardnum = input()
                    ## Check if card number passes Luhn Algo
                    checksum_cn=None
                    luhnAlgo_check(trans_cardnum)
                    if int(checksum)==int(checksum_cn):
                        ## Check if card number is legit by checking db
                        checkDB_transfer(trans_cardnum)
                        print(checked2)
                        if checked2 == True:
                            ## Ask for transfer amount
                            print('Enter how much money you want to transfer:')
                            amt_transfer=int(input())
                            ## Check if current acc balance is enough
                            get_balance(card_num)
                            print(new_bal)
                            curr_balance=new_bal
                            if curr_balance<amt_transfer:
                                print('Not enough money!')
                            else:
                                print('enough money')
                                get_balance(trans_cardnum)
                                print(curr_balance)
                                balance1_PostTrans = curr_balance - amt_transfer
                                print(balance1_PostTrans)
                                get_balance(trans_cardnum)
                                print(new_bal)
                                balance2_PreTrans = new_bal
                                balance2_PostTrans = balance2_PreTrans + amt_transfer
                                print(balance2_PostTrans)
                                #update db with the trans
                                UPDATE_BAL_SQL='''UPDATE card SET balance = ? WHERE number = ?'''
                                cur.execute(UPDATE_BAL_SQL,(balance2_PostTrans,trans_cardnum))
                                cur.execute(UPDATE_BAL_SQL,(balance1_PostTrans,card_num))
                                conn.commit()
                                #print balance
                                show_balance(card_num)
                        elif checked2 == False:
                            pass
                    else:
                        print('Probably you made a mistake in the card number. Please try again!')

                #4-'CLOSE ACCOUNT'
                elif m2inp == 4:

                    DELETE_ACC_SQL='''DELETE FROM card WHERE number = ?'''
                    cur.execute(DELETE_ACC_SQL,(card_num,))
                    conn.commit()
                    print('The account has been closed!')

                #5-'LOG OUT'
                elif m2inp == 5:
                    break
                #6-'EXIT'
                elif m2inp == 0:
                    exit()

        elif choice == '0':
            x = 0
            break
