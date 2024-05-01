"""
Anthony Silva
UNR, CPE 400, S24
friendship.py
class that represents a friendship. Currently not implemented. 
"""

from datetime import datetime

from identification import Identification

class Friendship:
    """
    object that shows a friendship exists
    """

    def __init__(
            self,
            sender : Identification,
            receiver : Identification
        ):
        self.sender = sender
        self.receiver = receiver
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    
    def get_sender(self) -> Identification:
        return self.sender
    
    def get_receiver(self) -> Identification:
        return self.receiver
    
    def get_datetime(self) -> str: 
        return self.datetime