import json
from copy import deepcopy

from identification import Identification
from message import Message
from exception import CustomException

class HashTable:

    """
    Class for holding message histories of client "friends"
    """

    def __init__(
            self,
            host : Identification
        ):
        # init stuff
        self.table = {}
        self.host = host
        self.fp = f"../data/{host.get_id()}_table.json"   

        # load hash table if it exists in memory, otherwise create new table
        try:
            self.load()
        except CustomException:
            self.table = {
                "host" : host.to_string(),
                "histories" : {}
            }
        
        


    def read_history(self, receiver : Identification) -> list:
        """
        read a history from the hashtable
        """
        # get receiver id
        receiver_id = receiver.get_id()

        # check if receiver id in table
        if receiver_id in self.table["histories"]:
            try: # try list grab
                history = self.table["histories"][receiver_id]["message_history"]
                better_history = []
                for entry in history:
                    better_history.append(Message.deserialize(entry))
                return better_history # return list
            except Exception: # list not found !
                # raise CustomException("Message History not found in receiver dictionary.")
                return []
        else: # id not found ! 
            # raise CustomException("ID not in table.")
            return []

    def write_message(self, message : Message, receive_flag: bool) -> int:
        """
        write a new message to a history, returns int based on execution status
        receive flag will be true when message being written is one received, in this case, the message history needs to be appended differently
        """

        # get data
        sender = message.get_sender()
        receiver = message.get_receiver()
        receiver_id = receiver.get_id()

        # check sender is right 
        if sender != self.host:
            # print("")
            # print("sender: " + str(sender))
            # print("table host: " + str(self.host))
            # print("table host id: " + str(self.host.get_id()))
            # print("sender id: " + str(sender.get_id()))
            # print("initial receiver id: " + str(receiver_id))
            # print("")
            if receive_flag: 
                # receiver is sender, sender is receiver
                receiver_id = sender.get_id() # swap receiver id with sender id so it is placed in the right history
            else:
                raise CustomException("Sender mismatch from message and table.")
        
        # check if receiver already in table
        if receiver_id in self.table["histories"]:
            
            # if in table, append to history

            self.table["histories"][receiver_id]["message_history"].append(message.serialize())
            return 1 # appended to entry
        else:
            # if not in table, create table appropriately 

            self.table["histories"][receiver_id] = {
                "name" : receiver.get_name(),
                "id" : receiver.get_id(),
                "ip" : receiver.get_ip(),
                "port" : receiver.get_port(),
                "receiver" : receiver.to_string(),
                "message_history" : [message.serialize(),]
            }
            return 0 # new entry made
    
    def overwrite_history(self, receiver : Identification, new_history : list):
        """
        completely overwrite a history 
        """
        # check if new history is empty
        if len(new_history) == 0:
            # do nothing
            return
        receiver_id = receiver.get_id()
        # check if receiver is in table
        if receiver_id not in self.table["histories"]:
            # not in table! create new entry and write the new history
            if isinstance(new_history[0], Message):
                self.table["histories"][receiver_id] = {
                    "name" : receiver.get_name(),
                    "id" : receiver_id,
                    "ip" : receiver.get_ip(),
                    "port" : receiver.get_port(),
                    "receiver" : receiver.to_string(),
                    "message_history" : deepcopy(Message.msg_history_prep(new_history))
                }
            else:
                self.table["histories"][receiver_id] = {
                    "name" : receiver.get_name(),
                    "id" : receiver_id,
                    "ip" : receiver.get_ip(),
                    "port" : receiver.get_port(),
                    "receiver" : receiver.to_string(),
                    "message_history" : deepcopy(new_history) # assuming it is already serialized 
                }
        else:
            # is in table, overwrite the history
            # overwrite hitsory
            if isinstance(new_history[0], Message):
                self.table["histories"][receiver_id]["message_history"] = Message.msg_history_prep(new_history)
            else:
                self.table["histories"][receiver_id]["message_history"] = new_history # assuming it is already serialized 

    def merge_history(self, receiver : Identification, new_history : list):
        """
        update a message history of a receiver to include any new messages in the new histry, (no duplicates)
        """
        # check if new history is empty
        if len(new_history) == 0:
            # do nothing
            return
        
        receiver_id = receiver.get_id()
        
        # check if receiver in table
        if receiver_id not in self.table["histories"]:
            # not in table! just overwrite and create new entry
            self.overwrite_history(receiver, new_history)
            return
        # get cur history
        cur_hist = self.table["histories"][receiver_id]["message_history"]

        # check if empty
        if len(cur_hist) == 0:
            # just overwrite
            self.overwrite_history(receiver, new_history)
            return
        
        # deserialize
        if not isinstance(cur_hist[0], Message):
            cur_hist = Message.msg_history_unprep(cur_hist)
        
        # merge histories
        new_hist = Message.merge_message_histories(cur_hist, new_history)

        # overwrite
        self.overwrite_history(receiver, new_hist)

        return
        

    def delete_history(self, receiver : Identification) -> int:
        """
        delete a history from the hashtable (clean slate!), overwrite with empty list, return int based on execution success
        """
        
        # get receiver id
        receiver_id = receiver.get_id()

        # check if receiver_id in table
        if receiver_id in self.table["histories"]:

            # if in table, check if history exists
            if "message_history" in self.table["histories"][receiver_id]:
                self.table["histories"][receiver_id]["message_history"] = []
                return 1 # successfully overwritted with empty list
            else:
                # if no message history, raise error
                raise CustomException("Message History not in table.")
        else:
            # if not in table, raise error
            raise CustomException("ID not in table.")

    
    def delete_receiver_entry(self, receiver : Identification) -> int:
        """
        delete entire receiver entry from hashtable (no longer friends)
        return int based on status of deletion execution
        """

        # get receiver id
        receiver_id = receiver.get_id()

        # check if receiver_id in table
        if receiver_id in self.table["histories"]:
            # if in table, remove it
            del self.table["histories"][receiver_id]
            return 1 # succesfully deleted
        else:
            return 0 # nothing to delete!


    
    def save(self):
        """
        save dict attribute to disk somewhere
        """
        try: 
            with open(self.fp, 'w') as file:
                json.dump(self.table, file)
        except Exception as e:
            raise CustomException(f"Unable to save to file! - {e}")
    
    def load(self):
        """
        load dict attribute from disk somewhere
        """
        try:
            with open(self.fp, 'r') as file:
                data = json.load(file)
                self.table = data
        except Exception as e:
            raise CustomException(f"Unable to load from file! - {e}")
