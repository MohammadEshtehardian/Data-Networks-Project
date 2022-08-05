import socket

class User:

    def __init__(self, id, interval, locations):
        self.id = id
        self.interval = interval
        self.locations = locations

    def __str__(self):
        return f"user id is: {self.id}\nuser interval is: {self.interval}\nuser locations is: {self.locations}"