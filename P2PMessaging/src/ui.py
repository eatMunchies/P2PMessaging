# imports
from identification import Identification
from client import Client
from live_connection import LiveConnection
from message import Message
import uuid # for MAC
import socket # for IP
from colorama import init, Fore, Back, Style

# colors
init(autoreset=True) # colorama init
RED = Fore.RED
GREEN = Fore.GREEN
BLUE = Fore.BLUE
PURPLE = Fore.MAGENTA
YELLOW = Fore.YELLOW
WHITE = Fore.WHITE
CYAN = Fore.CYAN
colors = [RED, GREEN, BLUE, PURPLE, YELLOW, WHITE, CYAN]

BRIGHT = Style.BRIGHT
DIM = Style.DIM 
NORMAL = Style.NORMAL
RESET = Style.RESET_ALL

# class

class UI:
    """
    class for displaying app capabilities to user 
    """

    def __init__(self):
        # get machine mac?
        self.mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 8)][::-1])
        # get machine ip
        self.ip = socket.gethostbyname(socket.gethostname())
        # ask for port user wants to use
        self.port = input("Enter what port you want to use for this conversation: ")

        # user port input check

        # self.port = int(self.port)

        # id stuff inniting
        self.name = input("What name do you want to use: ")
        # create id obj
        self.id = Identification(
            name = self.name,
            id = self.mac,
            ip = self.ip,
            port = self.port,
        )
        # create client obj with id
        self.client = Client(self.id)

        # useful lists
        self.menu_commands = ["quit", "add_connection",  "view_connection", "view_log"]
        self.connection_commands = ["quit", "send_message", "friend_status", "clear_history", "see_all_connections_view", "refresh"]
        self.running = False

    def mutuals(self):
        
        # init
        self.welcome_message()
        self.running = True
        self.client.start_listening() # start listening for requests in the background

        print(f"You are using IP: {self.ip}")
        print(f"You are using port: {self.port}")

        # main ui loop
        while self.running:
            try:
                menu_msg = "What would you like to do: "
                menu_cmd = self.menu_commands[UI.get_menu_option(menu_msg, self.menu_commands)]

                if menu_cmd == "add_connection":
                    self.add_conn()

                elif menu_cmd == "view_connection":
                    self.view_conn()

                elif menu_cmd == "view_log":
                    self.view_log()

                elif menu_cmd == "quit":
                    self.running = False
                    self.client.stop()
                    break
                else:
                    # error, bad command!
                    self.bad_option()

            except Exception as e:
                pass
            
        
        self.client.stop() # when loop is done, stop the client for cleanup
    
    def add_conn(self):
        peer_ip = input("Enter peer IP: ")
        peer_port = int(input("Enter peer port: "))
        peer_tuple = (peer_ip, peer_port)
        print(PURPLE + BRIGHT + self.client.start_conn(peer_tuple) + RESET)
    
    def view_conn(self):
        while self.running:
            conversation_names = []
            conversation_names.append("quit")
            for conn in self.client.connections:
                conversation_names.append(conn.get_receiver().get_name())
            conn_msg = "Select a conversation: \n"
            choice = UI.get_menu_option(conn_msg, conversation_names) - 1
            if choice == -1: # quit
                break
            conn_choice = self.client.connections[choice]
            leave = self.conn_menu(conn_choice) # leave == 1, quit option so break
            if leave: break
    
    def conn_menu(self, conn_choice : LiveConnection):
        while self.running:
            k = 10 # number of messages to printout
            self.print_message_history(conn_choice, k)
            # print("left message history")
            # get user input
            convo_message = "What would you like to do: "
            command = self.connection_commands[UI.get_menu_option(convo_message, self.connection_commands)]
            # print("got user input!")
            # handle user input
            if command == "send_message":
                content = input("Enter Message to Send: ")
                message = Message(self.id, conn_choice.get_receiver(), content, "TEXT_MESSAGE_REQUEST")
                self.client.send_message(message, conn_choice.get_socket(), conn_choice)
            elif command == "see_all_connections_view":
                return 0
            elif command == "friend_status":
                print("not implemented")
                continue
            elif command == "clear_history":
                print("not implemented")
                continue
            elif command == "quit":
                return 1
            elif command == "refresh":
                # read_receipt = Message(self.id, conn_choice.get_receiver(), "", "READ_RECEIPT")
                # self.client.send_message(read_receipt, conn_choice.get_socket(), conn_choice)
                continue
            else:
                print(RED + "Unknown Command! Try Again")
                continue
    
    def print_message_history(self, conn : LiveConnection, k : int):
        display_messages = []
        message_history = conn.get_history()
        top = len(message_history)
        # print("TOP: ", top)
        message_counter = 0
        types_to_display = ["TEXT_MESSAGE_REQUEST", "TEXT_MESSAGE_RESPONSE", "FRIEND_REQUEST", "FRIEND_RESPONSE", "END_FRIENDS", "READ_RECEIPT"]
        # get k most recent messages
        try:
            for i in reversed(range(top)):

                # print(message_history[i].get_type())
                msg = message_history[i]
                # print("Checking a message of type: ", msg.get_type())
                if not isinstance(msg, Message):
                    msg = Message.deserialize(msg)
                if msg.get_type() in types_to_display: # only append messages that should be displayed
                    # print("appended a type of ", msg.get_type())
                    display_messages.append(msg)
                    message_counter += 1
                if message_counter == k - 1: # stop considering messages after k amount of display type messages
                    print("breaking")
                    break
        except Exception as e:
            print(f"THE PROBLEM: {e}")
        # display conversation
        # print("MESSAGE COUNTER: ", message_counter)
        print(WHITE + BRIGHT + "***CONVERSATION WITH: " + conn.get_receiver().get_name() + "***\n" + RESET)
        for i in reversed(range(message_counter)):
            type = display_messages[i].get_type()
            time = display_messages[i].get_datetime() 
            content = display_messages[i].get_content()
            sender = display_messages[i].get_sender()
            receiver = display_messages[i].get_receiver()
            
            print(WHITE + NORMAL + "******************************" + RESET)
            print(PURPLE + BRIGHT + f"Type: {type}" + RESET)
            print(CYAN + BRIGHT + f"Time: {time}" + RESET)
            print(YELLOW + BRIGHT + f"From: {sender.get_name()}" + RESET)
            print(YELLOW + BRIGHT + f"To: {receiver.get_name()}" + RESET)
            print(BLUE + BRIGHT + f"Content: {content}" + RESET)
            print(WHITE + NORMAL + "******************************" + RESET)

    def view_log(self):
        # print("\nNOT IMPLEMENTED YET!\n")
        for conn in self.client.connections:
            print(f"HISTORY WITH {conn.get_receiver().get_name()}:", conn.get_history())

    def bad_option(self):
        print("\nBAD OPTION!\n")

    def welcome_message(self):
        print(
            BLUE + DIM + "***************************\n" +
            BLUE + DIM + "***" + PURPLE + BRIGHT + "WELCOME TO MUTUALS!!!" + RESET + DIM + BLUE + "***\n" +
            BLUE + DIM + "***************************\n" + RESET
        )

    @classmethod
    def print_menu(cls, list, n):
        color_index = 0
        num_colors = len(colors)
        for i in range(n):
            cur_color = colors[color_index]
            print(cur_color + BRIGHT + f"{i}: " + str(list[i]) + RESET)

            color_index += 1
            if color_index >= num_colors:
                color_index = 0
    
    @classmethod
    def get_menu_option(cls, message, commands):
        n = len(commands)

        while True:
            print("\n" + message)
            cls.print_menu(commands, n)
            raw_input = input(DIM + f"Enter command (0-{n-1}): ")

            try:
                option = int(raw_input)
            except Exception as e:
                print("B")
                print(RED + BRIGHT + "Not a valid input. Try again.")
                continue
            
            if 0 > option or n < option:
                print("A")
                print(RED + BRIGHT + "Not a valid input. Try Again.")
                continue

            return option