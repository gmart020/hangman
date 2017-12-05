import socket
import sys
from  threading import Thread
  
users = {'mango123' : 'pass1', 'apeking' : 'pass2', 'penisgrabber' : 'pass3'}
words = ['apple', 'cinammon', 'banana']
hall_of_fame = [('apeking', 10), ('mango123', 6), ('penisgrabber', 4)]  

def send_message(c, message):
    try:
        c.conn.send(message)
    except socket.error:
        print 'Send failed'
        sys.exit()

def receive_message(c):
    reply = c.conn.recv(1024)
    return reply

def make_socket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
    except socket.error as msg:
        sys.exit()
    s.listen(10)
    return s

def hall_fame(c):
    reply = '\n******************************\n'
    reply +=  '*          Hall of Fame      *\n'
    reply +=  '******************************\n'
    for i, member in enumerate(hall_of_fame, 1):
        reply += str(i) + '. ' + member[0] + '\tScore: ' + str(member[1]) + '\n'
    reply +=  '******************************'
    c.conn.send(reply)
    
def exit_game(c):
    reply = '******************************\n'
    reply +='*          Good Bye!         *\n'
    reply +='******************************\n'    
    send_message(c, reply)
    
def verify_login(c):
    prompt1 = 'Enter your username: '
    prompt2 = 'Enter your password: '
    error1 = 'ERROR: User name invalid. Please try again...'
    error2 = 'ERROR: Incorrect password for given user name. Please try again...'
    heading = '******************************\n'
    heading +='*           Login            *\n'
    heading +='******************************'
    username = ''
    message = heading + '_' + prompt1
    c.conn.send(message)
    while message != 'username valid':
        username = c.conn.recv(1024)
        if username in users:
            message = 'username valid'
        else:
            message = heading + '_' + error1 + '_' + prompt1
        c.conn.send(message)
        
    password = ''
    message = heading + '_' + prompt2
    c.conn.send(message)
    while message != 'password valid':
        password = c.conn.recv(1024)
        if users[username] != password:
            message = heading + '_' + error2 + '_' + prompt2
        else:
            message = 'password valid'
        c.conn.send(message)
        
    
class ClientThread(Thread):
    
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr

    def make_new_user(self, username, password):
        global users
        while username in users:
            reply = 'username exists'
            self.conn.send(reply)
            data = self.conn.recv(1024)
            username = data.split('_', 1)[1]
            
        users[username] = password
        self.conn.send('user created')

    def run(self): 
        while True:
            data = self.conn.recv(1024)
            request = data.split('_')
            if request[0] == 'login':
                verify_login(self)
            elif request[0] == 'make':
                self.make_new_user(request[1], request[2])
            elif request[0] == 'halloffame':
                hall_fame(self)
            elif request[0] == 'exit':
                exit_game(self)
                break
        self.conn.close()
        
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

def main_menu():
    print '\n******************************'
    print '*          Main Menu         *'
    print '******************************'
    print '1. Current list of users'
    print '2. Current list of words'
    print '3. Add a word'
    print '******************************'
    
def print_users():
    print '\n******************************'
    print '*           Users            *'
    print '******************************'
    for i, user in enumerate(users, 1):
        print str(i) + '. ' + str(user)
    print '******************************'
    
def print_words():
    print '\n******************************'
    print '*           Words            *'
    print '******************************'
    for i, word in enumerate(words, 1):
        print str(i) + '. ' + str(word)
    print '******************************'
    
def add_word():
    print ''
    new_word = raw_input('Enter new word to add to word list: ')
    print ''
    words.append(new_word)

while 1:
    main_menu()
    selection = int(raw_input('Choose an option: '))
    if selection == 1:
        print_users()
    elif selection == 2:
        print_words()
    elif selection == 3:
        add_word()
    else:
        pass
    