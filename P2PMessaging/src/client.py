"""
Anthony Silva
UNR, CPE 400, S24
client.py
Client class for performing all client related operations, like multiple connection management, history management, and more
"""

import socket
import threading
import logging
import errno

from live_connection import LiveConnection
from hash_table import HashTable
from friendship import Friendship
from identification import Identification
from message import Message

TIMEOUT = 5

class Client:
    """
    Handles Client Functionality of connecting to peers, maintaining connections, and closing connections
    """

    def __init__(
            self,
            id: Identification
        ):
        """
        Creates Client Obj
        """

        # data structures
        self.identification = id
        self.threads = []
        self.connections = []
        self.friends = {}
        self.hash_table = HashTable(self.identification)

        self.binding = (id.get_ip(), int(id.get_port()))

        # socket stuff
        self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening_socket.bind(self.binding)
        self.listening_socket.listen(5)
        # self.listening_socket.settimeout(TIMEOUT)

        # state
        self.running = True

        # logging
        self.logger = logging.getLogger('client_logger')
        self.file_handler = logging.FileHandler(f'../data/{self.identification.get_id()}_log.log')
        self.file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(self.file_formatter)
    
    def start_listening(self):
        """
        Create listening thread assigned to listen_for_connections
        """
        listening_thread = threading.Thread(target=self.listen_for_conns)
        listening_thread.start()
        self.threads.append(listening_thread)
        self.logger.info("Created listening thread")

    def listen_for_conns(self):
        """
        Listen for new connection requests, if new conn then create thread and go to handle conn
        """
        while self.running:
            try:
                # get connection
                client_socket, peer_tuple = self.listening_socket.accept()
                
                # thread this connection
                new_thread = threading.Thread(target=self.handle_conn, args=(client_socket, peer_tuple))
                new_thread.start()
                self.threads.append(new_thread)
                self.logger.info("Received new connection")
                print("Received new Connection!")

            except Exception as e:
                self.logger.error(f"Exception raised listening for connections: {e}")

    def start_conn(self, peer_tuple: tuple):
        """
        Start a connection request with someone, create a thread once accepted and go to handle conn
        """
        try:
            # create socket and connect
            receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            receiver_socket.connect(peer_tuple)

            # thread this connection
            new_thread = threading.Thread(target=self.handle_conn, args=(receiver_socket, peer_tuple))
            new_thread.start()
            self.threads.append(new_thread)
            self.logger.info("Started new connection")
            return "Created Connection!"

        except Exception as e:
            self.logger.error(f"Exception raised trying to start a connection: {e}")
            return "Failed Connection!"
    
    def init_conn(self, client_socket : socket.socket, peer_tuple : tuple) -> LiveConnection:
        """
        initialize a conversation, get peer id, name via begin conversation message, then go to handle_conn
        """

        try:
            # get ip, port
            receiver_ip, receiver_port = peer_tuple
            receiver_port = str(receiver_port)
            receiver_str = receiver_ip + ":" + receiver_port

            # prepare BEGIN CONVERSATION MESSAGE to get proper info
            receiver = Identification(
                name = receiver_str, # temp
                id = receiver_str, # temp
                ip = receiver_ip,
                port = receiver_port,
            )
            delimiter = "_*!*BEGINDELIM*!*_"
            begin_content = self.identification.get_name() + delimiter + self.identification.get_id() # send data in request message for efficiency
            begin_request_message = Message(self.identification, receiver, begin_content, "BEGIN_CONVERSATION_REQUEST")
            self.logger.info(f"Sent a message: {begin_request_message.serialize()}")

            # send begin message
            self.send_message(begin_request_message, client_socket)

            # listen for response
            while self.running:

                # receive a message
                begin_response_message = self.receive_message(client_socket)
                logging.info(f"Receieved a message: {begin_response_message.serialize()}")

                if begin_response_message.get_type() == "BEGIN_CONVERSATION_RESPONSE": # if message is a response to our request...

                    # get content from response message
                    data = begin_response_message.get_content() # standard format is name{delim}id
                    name, id = data.split(delimiter)

                    # update receiver, create connection
                    receiver.set_name(name)
                    receiver.set_id(id)
                    new_conn = LiveConnection(self.identification, receiver, client_socket)
                    self.connections.append(new_conn)
                    self.logger.info("Initted new connection with response")
                    # return
                    return new_conn
                
                elif begin_response_message.get_type() == "BEGIN_CONVERSATION_REQUEST": # if message is requesting us...

                    # while initting, if client sends request instead, respond accordingly
                    # get data from request
                    data = begin_response_message.get_content()
                    name, id = data.split(delimiter)

                    # update receiver, 
                    receiver.set_name(name)
                    receiver.set_id(id)
                    # send response 
                    new_begin_response_message = Message(self.identification, receiver, begin_content, "BEGIN_CONVERSATION_RESPONSE")
                    self.send_message(new_begin_response_message, client_socket)
                    self.logger.info("Sent begin convo response to request")
                    # create connection
                    new_conn = LiveConnection(self.identification, receiver, client_socket)
                    self.connections.append(new_conn)
                    self.logger.info("Initted new connection with request")
                    # return
                    return new_conn
                
                else:
                    continue # NEED SOME SORT OF TIMEOUT HERE IF FAILS
        
        except Exception as e:
            self.logger.error(f"Exception raised when intting a connection: {e}")
    
    def manage_histories(self, conn : LiveConnection):
        """
        see if history exists for this connection in self hash table
        if yes, update local history
        if no, send history request to receiver to see if they have anything
        """
        # print("\nconnection type: ", type(conn))
        receiver = conn.get_receiver()
        # print("\nreceiver type: ", type(receiver))
        history = self.hash_table.read_history(receiver)
        # print("\nhistory type: ", type(history))
        # print("\nhistory value: ", history)
        lotta_history = len(history) > 1 # is there more history than what was just sent?
        if lotta_history:
            # print("overwriting!")
            conn.overwrite_history(history)
            self.logger.info("found message history in hash table")
        else:
            # send history request to receiver later to see if they have anything
            # either can send request and handle response in handle_conn, or do same process as init conn, where look for requests/responses and manage flow from there based on message contents
            # print("placeholder for awesomeness!")
            # prepare hist request
            hist_rq_content = ""
            hist_rq_msg = Message(sender=self.identification, receiver=conn.get_receiver(), content=hist_rq_content, type="HISTORY_REQUEST")
            # send hist request
            self.send_message(hist_rq_msg, conn.get_socket(), conn)

            # handle message receptions
            while self.running:
                # receive message
                # print(type(conn))
                hist_response_msg = self.receive_message(conn.get_socket(), conn)
                logging.info(f"Receieved a message: {hist_response_msg.serialize()}")

                if hist_response_msg.get_type() == "HISTORY_RESPONSE":
                    # print("responsed!")
                    data_raw = hist_response_msg.get_content()
                    # unpackage data
                    data = Message.msg_history_unprep(data_raw)
                    # update self history if it not empty
                    # print("unpacke dmessage data looks like this: ", data)
                    if data != []:
                        # print("Overwrote")
                        # merge with current history
                        conn.merge_history(data)
                        # conn.overwrite_history(data)
                        # merge with hash table
                        self.hash_table.merge_history(receiver, data)
                    break   
                elif hist_response_msg.get_type() == "HISTORY_REQUEST":
                    # we are being requested, time to send what we have!
                    # print("requested!")
                    hist_raw = self.hash_table.read_history(conn.get_receiver())
                    hist_prep = Message.msg_history_prep(hist_raw)
                    # prepare response message
                    my_msg = Message(sender=self.identification, receiver=conn.get_receiver(), content=hist_prep, type='HISTORY_RESPONSE')
                    # send message
                    self.send_message(my_msg, conn.get_socket(), conn)
                    break
                else:
                    continue
                    # implement some sort of timeout here

            # handle hist responses + possible request to client
        self.logger.info("completed hash table check")
                    
    def handle_conn(self, client_socket : socket.socket, peer_tuple : tuple):
        """
        init conversation, get peer info to add it 
        receive messages from conn and handle message types. if conn appears 'dead' (timeout?), go to end_conn
            - types to handle:
                - TEXT_MESSAGE_REQUEST
                - FRIEND_REQUEST
                - END_FRIENDS
                - READ_RECEIPT
                - PULSECHECK_REQUEST
                - END_CONVERSATION_REQUEST
        if connection fails, go to end_conn
        """
        # init connection

        conn = self.init_conn(client_socket, peer_tuple)

        # print(type(conn))

        self.manage_histories(conn)

        # # # if there is message history
        # if history_exists:
        #     # prepare message w history
        #     hist_content_raw = conn.get_history()
        #     hist_content = Message.msg_history_prep(hist_content_raw)
        #     # hist_content = hist_content_raw
        #     hist_msg = Message(
        #         self.identification, conn.get_receiver(), hist_content, "HISTORY_REQUEST") 
        #     # send message
        #     self.send_message(hist_msg, client_socket, conn)

        # regular handling
        while self.running:
            try:
                # receive message
                message = self.receive_message(client_socket, conn)
                # handle message type
                if message.get_type() == "TEXT_MESSAGE_REQUEST":
                    self.text_message_rq_handler(message, conn)
                elif message.get_type() == "FRIEND_REQUEST":
                    self.friend_rq_handler(message, conn)
                elif message.get_type() == "END_FRIENDS":
                    self.end_friends_handler(message, conn)
                elif message.get_type() == "READ_RECEIPT":
                    self.read_receipt_handler(message, conn)
                elif message.get_type() == "PULSECHECK_REQUEST":
                    self.pulsecheck_rq_handler(message, conn)
                elif message.get_type() == "END_CONVERSATION_REQUEST":
                    self.end_conversation_rq_handler(message, conn)
                    break
                elif message.get_type() == "HISTORY_REQUEST":
                    self.history_rq_handler(message, conn)
                else:
                    # logging message was nothing, or bad
                    self.bad_message_handler(message, conn)

            except Exception as e:
                self.logger.error(f"Exception raised when handling connection: {e}")

        # end conn
        self.end_conn(conn)

    def end_conn(self, conn : LiveConnection):
        """
        envoke a connection end, send message, then go to cleanup conn
        """

        # check if connection is already ended
        def is_socket_closed(sock):
            try:
                sock.settimeout(0.5)
                data = sock.recv(16)
                if not data:
                    return True
            except socket.timeout:
                return False
            except socket.error as e:
                return e.errno != errno.EAGAIN
            except:
                return False
            return True
        
        if not is_socket_closed(conn.get_socket()):
            # send message
            end_msg = Message(
                    sender=conn.get_sender(),
                    receiver=conn.get_receiver(),
                    content="Bye bye now!",
                    type="END_CONVERSATION_REQUEST",
                )
            self.send_message(end_msg, conn.get_socket(), conn)
            # cleanup conn
            self.cleanup_conn(conn)


    def cleanup_conn(self, conn : LiveConnection):
        """
        cleanup conn, thread, and other stuff
        """
        # remove conn
        conn.get_socket().close()
        if conn in self.connections:
            self.connections.remove(conn)
        # remove thread

        # other stuff

    def send_message(self, message : Message, csocket : socket.socket, conn : LiveConnection = None): 
        """
        send a message obj to someone
        conn is None if BEGIN convo request
        """

        try:

            # prepare data 
            data = message.prepare_send()
            data_len = len(data).to_bytes(4, 'big')

            # send data through socket
            csocket.sendall(data_len + data)

            # update local records
            if conn:
                conn.add_message(message)
            self.hash_table.write_message(message, False) # need to do this only if person is "friend"
            self.logger.info(f"Successfully sent message to {message.get_receiver().get_id()}")

        except Exception as e:
            self.logger.error(f"Exception raised when sending message: {e}")

    def receive_message(self, csocket : socket.socket, conn : LiveConnection = None) -> Message: 
        """
        receive a message obj from someone
        conn is None if BEGIN convo response
        """

        try:
            # read message len first
            raw_msg_len = csocket.recv(4)
            if not raw_msg_len:
                raise Exception("No message length!")
            msg_len = int.from_bytes(raw_msg_len, 'big')
            # get bytes of full message
            full_msg = b''
            while len(full_msg) < msg_len:
                part = csocket.recv(msg_len - len(full_msg))
                if not part:
                    raise Exception("Conn closed b4 full message could be read!")
                full_msg += part
            # get data, prepare for message
            message = Message.prepare_receive(full_msg)

            # update local records
            if conn:
                conn.add_message(message)
            self.hash_table.write_message(message, True) # need to do this only if person is "friend"
            self.logger.info(f"Successfully received message from {message.get_sender().get_id()}")

            # return message
            return message
        
        except Exception as e:

            err_msg = f"Exception raised when receiving message: {e}"
            self.logger.error(err_msg)
            print(err_msg)
            message = Message(self.identification, conn.get_receiver(), err_msg, "ERROR")

            return message
    
    def stop(self):
        """
        turn off app, do total cleanup
        """
        try:
            self.running = False
            # connections
            for conn in self.connections:
                end_msg = Message(
                    sender=conn.get_sender(),
                    receiver=conn.get_receiver(),
                    content="Bye bye now!",
                    type="END_CONVERSATION_REQUEST",
                )
                self.send_message(end_msg, conn.get_socket(), conn)
                conn.get_socket().close()
            # threads
            for thread in self.threads:
                thread.join(timeout=1)
        except:
            pass 

    """
    Message handlers
    """

    def text_message_rq_handler(self, msg : Message, conn : LiveConnection):
        pass

    def end_conversation_rq_handler(self, msg : Message, conn : LiveConnection):
        self.connections.remove(conn)
        print("\nConnection with " + conn.get_receiver().get_name() + " ended.\n")

    def friend_rq_handler(self, msg : Message, conn : LiveConnection):
        pass 
    
    def end_friends_handler(self, msg : Message, conn : LiveConnection):
        pass 

    def read_receipt_handler(self, msg : Message, conn : LiveConnection):
        pass 

    def pulsecheck_rq_handler(self, msg : Message, conn : LiveConnection):
        pass

    def bad_message_handler(self, msg : Message, conn : LiveConnection):
        pass

    def history_rq_handler(self, msg : Message, conn : LiveConnection):
        """
        
        """
        # we are being requested, time to send what we have!
        hist_raw = self.hash_table.read_history(conn.get_receiver())
        hist_prep = Message.msg_history_prep(hist_raw)
        # prepare response message
        my_msg = Message(sender=self.identification, receiver=conn.get_receiver(), content=hist_prep, type='HISTORY_RESPONSE')
        # send message
        self.send_message(my_msg, conn.get_socket(), conn)