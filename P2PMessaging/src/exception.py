

class CustomException(Exception):
    """
    Raise exception with custom message
    """
    def __init__(self, message : str):
        self.message = message