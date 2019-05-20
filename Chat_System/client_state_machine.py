"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def game(self,peer):
        msg = json.dupms({"action":"game_request","target":peer})
        mysend(self.s,msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += "You are now playing game with " + self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot play with yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def leavegame(self):
        msg = json.dumps({"action":"leave_game","peer":self.peer})
        mysend(self.s,msg)
        self.out_msg += "You quit the game with " + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    # print(poem)
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

                elif my_msg[0] == 'g':
                    peer = my_msg][1:]
                    peer = peer.strip()
                    if self.game(peer) == True:
                        self.state = S_GAMING
                        self.out_msg += 'Playing game with ' + peer + ' now! Have Fun!\n\n'
                        self.out_msg += '-----------------------------------\n'
                else:
                    self.out_msg += 'Playing with ' + peer + 'unsuccessfully\n'
                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                try:
                    peer_msg = json.loads(peer_msg)
                except Exception as err :
                    self.out_msg += " json.loads failed " + str(err)
                    return self.out_msg

                if peer_msg["action"] == "connect":
                    # IMPLEMENTATION
                    # ---- start your code ---- #

                    peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + peer + '\n'
                    self.out_msg += 'You are connect with ' + peer + '. Chat away!\n'
                    self.out_msg += '-----------------------------------\n'
                    self.state = S_CHATTING

                    # ---- end of your code --- #
                if peer_msg["action"] == "game_request":
                    peer = peer_msg["from"]
                    self.out_msg += 'Game request from ' + peer + '\n'
                    self.out_msg += 'You are playing game with ' + peer + '. Have Fun!\n'
                    self.out_msg += '-----------------------------------\n'
                    self.state = S_GAMING


#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                # IMPLEMENTATION
                # ---- start your code ---- #

                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    peer = peer_msg["from"]
                    self.out_msg += '(' + peer + ' joined)\n'
                if peer_msg["action"] == "exchange":
                    peer = peer_msg["from"]
                    message = peer_msg['message']
#                    said = text_proc(message, peer)
#                   self.indices[peer].add_msg_and_index(said)
                    self.out_msg += '[' + peer + ']' + message
                if peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                    self.out_msg = "everyone left, you are alone\n"

                # ---- end of your code --- #
            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu


# ==============================================================================
# Start playing, 'bye' for quit
# This is event handling instate "S_GAMING"
# ==============================================================================
        elif self.state == S_GAMING:
            if len(my_msg) > 0:
                mysend(self.s,json.dumps({"action":"gaming", "from":"[" + self.me + "]", "message":my_msg}))
                if my_msg == 'bye':
                    self.leavegame()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:
                peer_msg = json.load(peer_msg)
                if peer_msg["action"] == "leave_game":
                    self.state = S_LOGGEDIN
                    self.out_msg = "Your peer leave the game, you are alone\n"
                if peer_msg["action"] == "gaming":

                    self.out_msg += prt()
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
