import socket

class SGW:

    def __init__(self, max_entry):
        self.buffer = []
        self.ENB = []
        self.routing_table = {}
        self.max_entry = max_entry