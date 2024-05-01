"""
Anthony Silva
UNR, CPE 400, S24
message.py
Message class that holds message information. Provides a standard interface for all message types. 
"""

from datetime import datetime
import json 

from identification import Identification

class Message:
    """
    holds message info
    """

    encoding = "utf-8"
    standard_types = [
        "BEGIN_CONVERSATION_REQUEST",
        "BEGIN_CONVERSATION_RESPONSE",
        #
        "END_CONVERSATION_REQUEST",
        "END_CONVERSATION_RESPONSE",
        #
        "TEXT_MESSAGE_REQUEST",
        "TEXT_MESSAGE_RESPONSE",
        #
        "FRIEND_REQUEST", # friend stuff will be implemented later
        "FRIEND_RESPONSE",
        #
        "END_FRIENDS",
        #
        "HISTORY_REQUEST",
        "HISTORY_RESPONSE",
        #
        "READ_RECEIPT",
        #
        "ERROR",
        #
        "PULSECHECK_REQUEST", # will be removed
        "PULSECHECK_RESPONSE", # will be removed
    ]

    def __init__(
            self,
            sender: Identification,
            receiver: Identification,
            content: str,
            type: str,
            dt: str = None,
        ):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.type = type
        if dt:
            self.datetime = dt
        else:
            self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def serialize(self) -> str:
        """
        put a message obj into json dumps string format for sending
        """
        return json.dumps({
            "sender" : self.sender.to_string(),
            "receiver" : self.receiver.to_string(),
            "content" : self.content,
            "type" : self.type,
            "datetime" : self.datetime,
        })

    @classmethod
    def deserialize(cls : object, json_str : str) -> object:
        """
        create a message obj from json dumps string format
        """
        data = json.loads(json_str)
        return cls(
            sender=Identification.from_string(data["sender"]),
            receiver=Identification.from_string(data["receiver"]),
            content=data["content"],
            type=data["type"],
            dt=data["datetime"],
        )

    @classmethod
    def encode_msg(cls : object, message : str) -> bytes:  
        """
        encode message for sending
        """
        return message.encode(cls.encoding)

    @classmethod
    def decode_msg(cls : object, message : bytes) -> str:
        """
        decode message for receiving
        """
        return message.decode(cls.encoding)

    @classmethod
    def msg_history_prep(cls : object, hist : list):
        # print("prep")
        # print("Type of hist_content_raw:", type(hist))
        # print("Value of hist_content_raw:", hist)
        return [obj.serialize() for obj in hist]

    @classmethod
    def msg_history_unprep(cls : object, hist : list):
        # print("unprep")
        # print("Type of hist_content_raw:", type(hist))
        # print("Value of hist_content_raw:", hist)
        return [cls.deserialize(obj) for obj in hist]
    
    @staticmethod
    def merge_message_histories(histA : list, histB : list):
        """
        merge two histories, sorted on datetime, no duplicates
        """
        # first make sure lists are unserialized
        if not isinstance(histA[0], Message):
            histA = Message.msg_history_unprep(histA)
        
        if not isinstance(histB[0], Message):
            histB = Message.msg_history_unprep(histB)
        
        # make combined list
        hist = histA + histB

        # remove duplicates using a dictionary + hash to track unique message representations
        unique_messages = {}
        for message in hist:
            # Create a unique key based on attributes that define uniqueness
            message_key = str(
                str(message.get_sender().to_string()) 
                + str(message.get_receiver().to_string())
                + str(message.get_content()) 
                + str(message.get_type()) 
                + str(message.get_datetime()))
            if message_key not in unique_messages:
                unique_messages[message_key] = message
        hist = list(unique_messages.values())
        # sort on datetime
        hist.sort(key=lambda msg: datetime.strptime(msg.get_datetime(), "%Y-%m-%d %H:%M:%S"))
        # return
        return hist

    def prepare_send(self):
        """
        prepare a message obj for send across socket
        """
        return self.encode_msg(self.serialize())

    @classmethod
    def prepare_receive(cls : object, msg : bytes) -> object:
        """
        create a msg obj for reception from socket
        """
        return cls.deserialize(cls.decode_msg(msg))
    
    def get_sender(self) -> Identification:
        return self.sender

    def get_receiver(self) -> Identification:
        return self.receiver

    def get_content(self) -> str:
        return self.content

    def get_type(self) -> str:
        return self.type
    
    def get_datetime(self) -> str:
        return self.datetime