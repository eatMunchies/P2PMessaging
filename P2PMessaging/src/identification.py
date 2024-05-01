


class Identification:

    """
    class for encapsulating all info that identifies a client
    """

    delimiter = "_*!*ID*!*DELIM*!*_"

    def __init__(
            self,
            name : str,
            id : str,
            ip : str,
            port : str,
        ):
        self.name = name
        self.id = id
        self.ip = ip
        self.port = port

    def to_string(self) -> str:
        to_str = self.delimiter.join([self.name, self.id, self.ip, self.port])
        return to_str
    
    @classmethod
    def from_string(cls : object, from_str : str) -> object:
        name, id, ip, port = from_str.split(cls.delimiter)
        return cls(name, id, ip, port)

    def get_name(self) -> str:
        return self.name
    
    def get_id(self) -> str:
        return self.id
    
    def get_ip(self) -> str:
        return self.ip

    def get_port(self) -> str:
        return self.port
    
    def set_name(self, name : str):
        self.name = name
    
    def set_id(self, id : str):
        self.id = id
    
    def __eq__(self, other):
        if not isinstance(other, Identification):
            # Not comparable if 'other' is not a Book
            return NotImplemented
        
        return (self.id == other.id)