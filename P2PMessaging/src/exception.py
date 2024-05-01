"""
Anthony Silva
UNR, CPE 400, S24
exception.py
this class is kind of useless. will be deprecated in later versions. 
"""

class CustomException(Exception):
    """
    Raise exception with custom message
    """
    def __init__(self, message : str):
        self.message = message