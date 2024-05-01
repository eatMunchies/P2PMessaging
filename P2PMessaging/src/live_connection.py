from copy import deepcopy
from datetime import datetime

from identification import Identification
from message import Message

class LiveConnection:
    """
    Class for holding info of a single connection
    """

    def __init__(
            self,
            sender : Identification,
            receiver : Identification,
            socket,
        ):
        self.sender = sender
        self.receiver = receiver
        self.socket = socket
        self.message_history = []
    
    def add_message(self, new_msg : Message):
        """
        Add a message to history 
        """
        # self.message_history.append(new_msg.serialize()) # TEST
        self.message_history.append(new_msg) # TEST

    def overwrite_history(self, new_history : list):
        """
        overwrite message history entirely
        """
        self.message_history = deepcopy(new_history)
    
    def merge_history(self, new_history : list):
        """
        merges new history list and self message history to have no duplicates and sort on time
        """

        # if self.empty, just get the new list
        if len(self.message_history) == 0:
            self.overwrite_history(new_history)

        self.message_history = Message.merge_message_histories(self.message_history, new_history)
    
    def get_socket(self):
        return self.socket

    def get_history(self) -> list:
        return self.message_history
    
    def get_sender(self) -> Identification:
        return self.sender
    
    def get_receiver(self) -> Identification:
        return self.receiver