import socket
import sys
from  threading import Thread
  
def make_socket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
    except socket.error as msg:
        sys.exit()
    s.listen(10)
    return s

class ClientThread(Thread):
    
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr

    def run(self): 
        while True:
            data = self.conn.recv(1024)
            reply = 'OK...' + data
            self.conn.send(reply)
        conn.close()
        
class ConnectionListener(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        self.s = make_socket('', 8888)
        
    def run(self):
        while 1:
            conn, addr = self.s.accept()
            client = ClientThread(conn, addr)
            client.start()
        self.s.close()
    
thread = ConnectionListener()
thread.start()

users = {'mango123' : 'pass1', 'apeking' : 'pass2'}
words = ['apple', 'cinammon', 'banana']

def main_menu():
    print 'Main Menu'
    print '\t1. Current List of Users'
    print '\t2. Current List of Words'
    print '\t3. Add new word to the list of words.'
    
def print_users():
    print '\nUsers'
    print '--------------------------'
    for i, user in enumerate(users, 1):
        print str(i) + '. ' + str(user)
    print ''
    
def print_words():
    print '\nWords'
    print '--------------------------'
    for i, word in enumerate(words, 1):
        print str(i) + '. ' + str(word)
    print ''
    
def add_word():
    print ''
    new_word = raw_input('Enter new word to add to word list: ')
    print ''
    words.append(new_word)

while 1:
    main_menu()
    selection = int(raw_input('\tChoose an option: '))
    if selection == 1:
        print_users()
    elif selection == 2:
        print_words()
    elif selection == 3:
        add_word()
    else:
        pass
    