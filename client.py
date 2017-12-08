import os
import getpass
import sys
import socket
import threading

def main_menu():
    print '\n******************************'
    print '*          Main Menu         *'
    print '******************************'
    print '1. Login'
    print '2. Make New User'
    print '3. Hall of Fame'
    print '4. Exit'
    print '******************************'
    
HOST = '127.0.0.1'
PORT = 8888

name = ''

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
    print 'Failed to create socket.'
    sys.exit()
    
s.connect((HOST, PORT))

def send_message(message):
    global s
    try:
        s.send(message)
    except socket.error:
        print 'Send failed'
        sys.exit()

def receive_message():
    global s
    reply = s.recv(4096)
    return reply
    
def new_user():
    prompt1 = 'What is your user name?: '
    prompt2 = 'What is your password?: '
    response = ''
    while response != 'user created':
        print '******************************'
        print   '*      Create New User       *'
        print   '******************************'
        if response == 'username exists':
            print 'ERROR: Username already exits. Please try again...'
        username = raw_input(prompt1)
        password = getpass.getpass(prompt2)
        message = 'make' + '_' + username + '_' + password
        send_message(message)
        response = receive_message()
        
    print  '\n******************************'
    print   '* User Created Successfully  *'
    print   '******************************'
    
def hall_of_fame():
    request = 'halloffame'
    send_message(request)
    response = receive_message()
    print response
    
def exit_game():
    request = 'exit'
    send_message(request)
    response = receive_message()
    print response
    s.close()
    sys.exit()
    
def join_game():
    response = receive_message()
    response = response.split(':')
    while response[0] != 'game over':
        global name
        print ''
        print response[0]
        input = raw_input('Enter your guess: ')
        reply = input + ':' + name 
        send_message(reply)
        response = receive_message()
        response = response.split(':')
        
    print response[1]
    
def start_game():
    response = receive_message()
    response = response.split(':')
    while response[0] != 'game over':
        global name
        print ''
        print response[0]
        input = raw_input('Enter your guess: ')
        reply = input + ':' + name 
        send_message(reply)
        response = receive_message()
        response = response.split(':')
        
    print response[1]
        
def select_difficulty():
    request = 'select difficulty'
    send_message(request)
    resp = receive_message()
    print resp
    selection = raw_input('Choose an option: ')
    if int(selection) > 3:
        selection = '1'
    send_message(selection)
    start_game()

def get_games():
    request = 'getgames'
    send_message(request)
    response = receive_message()
    response = response.split('>')
    print response[0]
    if len(response) > 1:
        return
    else:
        selection = raw_input('Choose a game to join: ')
        send_message(selection)
        join_game()

def back_to_main():
    request = 'log out'
    send_message(request)
    global name
    name = ''
  
def game_menu():
    send_message('login menu')
    menu = receive_message()
    while 1:
        print ''
        print menu
        selection = int(raw_input('Choose an option: '))
        
        if selection == 1:
            select_difficulty()
        elif selection == 2:
            get_games()
        elif selection == 3:
            #finished
            hall_of_fame()
        elif selection == 4:
            #finished
            back_to_main()
            return
        else:
            pass
        
        selection = 0
    
def login():
    request = 'login'
    send_message(request)
    response = receive_message()
    response = response.split('_')
    heading = response[0]
    prompt1 = response[1]
    error1 = response[2]
    prompt2 = response[3]
    error2 = response[4]
    confirmation = response[5]
    
    print heading
    username = raw_input(prompt1)
    send_message(username)
    response = receive_message()
    
    while response != 'username valid':
        print ''
        print heading
        print error1
        username = raw_input(prompt1)
        send_message(username)
        response = receive_message()
        
    print ''
    print heading
    password = getpass.getpass(prompt2)
    send_message(password)
    response = receive_message()
    
    while response != 'password valid':
        print ''
        print heading
        print error2
        password = getpass.getpass(prompt2)
        send_message(password)
        response = receive_message()
        
    print ''
    print confirmation
    global name
    name = username
    game_menu()
        
while 1:
    main_menu()
    selection = int(raw_input('Enter an option: '))
    print ''
    if selection == 1:
        login()
    elif selection == 2:
        new_user()
    elif selection == 3:
        hall_of_fame()
    elif selection == 4:
        exit_game()
    else:
        pass

