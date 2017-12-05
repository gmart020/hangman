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
    reply = s.recv(1024)
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
        
    print  '******************************'
    print   '* User Created Successfully  *'
    print   '******************************'
    
def hall_of_fame():
    request = 'halloffame_'
    send_message(request)
    response = receive_message()
    print response
    
def exit_game():
    request = 'exit_'
    send_message(request)
    response = receive_message()
    print response
    s.close()
    sys.exit()
    
def login():
    request = 'login'
    send_message(request)
    response = receive_message()
    response = response.split('_')
    while response[0] != 'username valid':
        print response[0]
        if len(response) > 2:
            print response[1]
            username = raw_input(response[2])
        else:
            username = raw_input(response[1])
        send_message(username)
        response = receive_message()
        response = response.split('_')
        
    response = receive_message()
    response = response.split('_')
    while response[0] != 'password valid':
        print response[0]
        if len(response) > 2:
            print response[1]
            password = raw_input(response[2])
        else:
            password = raw_input(response[1])
        send_message(password)
        response = receive_message()
        response = response.split('_')

    
    print 'complete'
    
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

