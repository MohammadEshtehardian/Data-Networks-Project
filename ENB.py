import socket

class ENB:

    def __init__(self, uid, coordinate):
        self.uid = uid
        self.buffer = []
        self.coordinate = coordinate

    def __str__(self):
        return f"uid is: {self.uid}\ncoordinate is: {self.coordinate}"