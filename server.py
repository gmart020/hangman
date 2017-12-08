import socket
import sys
from  threading import Thread
import random
import uuid
import select
from threading import Lock

game_lock = Lock()
users = {'mango123' : 'pass1', 'apeking' : 'pass2', 'penisgrabber' : 'pass3'}
words = ['apple', 'cinammon', 'banana']
hall_of_fame = [('apeking', 10), ('mango123', 6), ('penisgrabber', 4)] 
active_games = []
you_lose = '\n******************************\n   You Guessed Wrong\n******************************\n'

class Game(Thread):
    
    def __init__(self, difficulty, player):
        self.lck = Lock()
        tmp = player.get_name()
        self.player_list = {}
        self.score_list = {}
        self.order_list = []
        # EASY = 1, MEDIUM = 2, HARD = 3
        self.difficulty = difficulty
        self.word = words[random.randint(0, len(words) - 1)]
        self.cur_word = self.encrypt()
        self.turn = 0
        self.max_guess = self.select_max()
        self.guessed = set()
        self.add_player(player, tmp)
    
    def select_max(self):
        if self.difficulty == 1:
            return len(self.word) * 3
        elif self.difficulty == 2:
            return len(self.word) * 2
        else:
            return len(self.word)
    
    def get_socks(self):
        socks = []
        self.lck.acquire()
        for player in self.player_list:
            socks.append(self.player_list[player].conn)
        self.lck.release()
        return socks
    
    def encrypt(self):
        result = ''
        for ch in self.word:
            result += '_'
        return result
        
    def add_player(self, player, name):
        self.lck.acquire()
        self.player_list[name] = player
        self.order_list.append(name)
        self.score_list[name] = 0
        self.lck.release()
        
    def remove_player(self, name):
        self.lck.acquire()
        del self.player_list[name]
        self.order_list.remove(name)
        del self.score_list[name]
        self.lck.release()
        
    def game_state(self):
        screen = '******************************\n'
        screen +='          Hangman             \n'
        screen +='******************************\n'
        self.lck.acquire()
        screen = screen + ' '.join(list(self.cur_word))
        screen += '\n\n'
        for i, ch in enumerate(list(self.guessed), 1):
            screen += ch
            screen += ' '
            if i % len(self.word) == 0:
                screen += '\n'

        screen += '\n\n'
        
        for i, player in enumerate(self.order_list):
            screen = screen + player + ' ' + str(self.score_list[player])
            if i == self.turn:
                screen += ' *'
            screen += '\n'
        self.lck.release()
        return screen
        
    def get_info(self):
        self.lck.acquire()
        w = ' '.join(list(self.cur_word))
        d = ''
        if self.difficulty == 1:
            d = 'Easy'
        elif self.difficulty == 2:
            d = 'Medium'
        else:
            d = 'Hard'
        players = ', '.join(self.order_list)
        self.lck.release()
        result = w + '\n' + 'Difficulty: ' + d + '\n' + 'Players: ' + players + '\n' 
        return result
        
    def handle_guess(self, guess, player):
        #if player == self.order_list[self.turn]:
        if len(guess) > 1:
            if guess != self.word:
                return -1
            else:
                self.cur_word = self.word
                self.score_list[player] += len(self.word)
                return 2
        elif len(guess) == 0:
            return 0
        else:
            if player == self.order_list[self.turn]:
                if guess in self.guessed or guess in self.cur_word:
                    return 0
                else:
                    if guess in self.word:
                        tmp = []
                        for i, ch in enumerate(self.word):
                            if ch == guess:
                                tmp.append(guess)
                                self.score_list[player] += 1
                            elif self.cur_word[i] != '_':
                                tmp.append(ch)
                            else:
                                tmp.append('_')
                        self.lck.acquire()
                        self.cur_word = ''.join(tmp)
                        self.lck.release()
                        if '_' not in self.cur_word:
                            return 2
                        else:
                            return 1
                    else:
                        self.guessed.add(guess)
                        if len(self.guessed) == self.max_guess:
                            return -2
            return 3
            
    def send_state(self):
        state = self.game_state()
        for player in self.player_list:
            message = state
            self.player_list[player].conn.send(message)
                            
    def start(self):
        self.send_state()
        while 1:
            socks = self.get_socks()
            print socks
            reads, writes, errors = select.select(socks, [], [])
            print reads
            while not reads:
                pass
                # #idk what this does
                # socks = self.get_socks()
                # reads, writes, errors = select.select(socks, [], [])
            #recieve response from a client
            response = reads[0].recv(1024)
            response = response.split(':')
            print response

            guess = response[0]
            sender = response[1]
            result = self.handle_guess(guess, sender)
            
            if result == -1:
                self.player_list[sender].conn.send('game over:' + you_lose)
                self.remove_player(sender)
                self.send_state()
                if self.turn >= len(self.order_list) and len(self.order_list) > 0:
                    self.turn = 0
                else:
                    active_games.remove(self)
                    # All players lost
                    return 
            elif result == -2:
                message = 'game over:'
                message += '\n******************************\n'
                message +='  Max Guess Attempts Reached\n'
                message +='          Game Over\n'
                message +='******************************\n\n'
                message += self.game_state()
                for i, player in enumerate(self.player_list):
                    self.player_list[player].conn.send(message)
                game_lock.acquire()
                active_games.remove(self)    
                game_lock.release()
                return
                
            elif result == 0:
                if self.turn == len(self.order_list) - 1:
                    self.turn = 0
                else:
                    self.turn += 1
                    
                self.send_state()
                    
            elif result == 2:
                message = 'game over:'
                message += '\n******************************\n      '
                message += sender
                message += ' Wins\n'
                message +='******************************\n\n'
                message += self.game_state()
                for i, person in enumerate(self.player_list):
                    self.player_list[person].conn.send(message)
                game_lock.acquire()
                active_games.remove(self)    
                game_lock.release()
                return
            elif result == 3:
                self.send_state()
            else:
                self.send_state()
                
            response = []
                    
                    
                
            
            
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
    confirmation = '******************************\n'
    confirmation +='       User logged in.\n'
    confirmation +='******************************'
    
    message = heading + '_' + prompt1 + '_' + error1 + '_' + prompt2 + '_' + error2 + '_' + confirmation
    c.conn.send(message)
    username = c.conn.recv(1024)
    
    while not (username in users):
        c.conn.send('username invalid')
        username = c.conn.recv(1024)
        
    c.conn.send('username valid')
    password = c.conn.recv(1024)
    
    while users[username] != password:
        c.conn.send('password invalid')
        password = c.conn.recv(1024)
    
    c.set_name(username)
    c.set_score(0)
    c.conn.send('password valid')
    
def get_games(c):
    result = '\n******************************\n'
    result +='       Active Games         \n'
    result +='******************************\n'
    
    if len(active_games) > 0:
        game_lock.acquire()
        for i, game in enumerate(active_games, 1):
            result = result + str(i) + '. ' + game.get_info() + '\n'
        game_lock.release()
    else:
        result += 'No Games\n'
        result += '>NADA'
        c.conn.send(result)
        return
    c.conn.send(result)
    selection = c.conn.recv(1024)
    selection = int(selection) - 1
    game_lock.acquire()
    active_games[selection].add_player(c, c.get_name())
    game_lock.release()
        
   

def game_play(client, difficulty):
    game = Game(difficulty, client)
    game_lock.acquire()
    active_games.append(game)
    game_lock.release()
    game.start()

def get_difficulty(c):
    menu = '\n******************************\n'
    menu +='      Choose Difficulty       \n'
    menu +='******************************\n'
    menu +='1. Easy\n'
    menu +='2. Medium\n'
    menu +='3. Hard\n'
    menu +='******************************'

    c.conn.send(menu)
    response = c.conn.recv(1024)
    difficulty = int(response)
    #name = c.get_name()
    #c.conn.send(name)
    game_play(c, difficulty)
    
def game_menu(c):
    menu = '*****************************\n'
    menu += '           Game Menu          \n'
    menu += '******************************\n'
    menu += '1. Start New Game\n'
    menu += '2. Get List of Games\n'
    menu += '3. Hall of Fame\n'
    menu += '4. Exit\n'
    menu += '******************************' 
    request = c.conn.recv(1024)
    c.conn.send(menu)
    while 1:
        #wait for option selection
        request = c.conn.recv(1024)
        request = request.split('_')
        if request[0] == 'select difficulty':
            get_difficulty(c)
        elif request[0] == 'getgames':
            get_games(c)
        elif request[0] == 'halloffame':
            hall_fame(c)
        elif request[0] == 'log out':
            c.set_name('')
            c.set_score(0)
            return
        else:
            pass
        
        request = ''
    
class ClientThread(Thread):
    
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.username = ''
        self.score = 0
        
    def get_name(self):
        return self.username
        
    def get_score(self):
        return self.score
        
    def get_id(self):
        return self.id
        
    def set_name(self, name):
        self.username = name
        
    def set_score(self, score):
        self.score = score

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
                game_menu(self)
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
    