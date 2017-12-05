import os
import getpass
import sys
import socket
import threading

def main_menu():
    print ''
    print 'Main Menu'
    print '\t1. Login'
    print '\t2. Make New User'
    print '\t3. Hall of Fame'
    print '\t4. Exit'
    print ''
    
HOST = '127.0.0.1'
PORT = 8888

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
    print 'Failed to create socket.'
    sys.exit()
    
s.connect((HOST, PORT))

def send(message)
    global s
    try:
        s.send(message)
    except socket.error:
        print 'Send failed'
        sys.exit()
    reply = s.recv(4096)
    return reply

    
def new_user_menu():
    print ''
    username = raw_input('What is your user name?\n')
    msg = 'm_' + username
    response = send(msg)
    print response
    password = getpass.getpass('What is your password?\n')
    print ''
    return (username, password)
    
while 1:
    main_menu()
    selection = int(raw_input('\tEnter an option: '))
    print ''
    if selection == 1:
        pass
    elif selection == 2:
        username, password = new_user_menu()
        request = 'm_' + username 
    elif selection == 3:
        pass
    elif selection == 4:
        pass
    else:
        pass

