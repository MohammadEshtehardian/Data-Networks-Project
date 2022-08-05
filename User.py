import socket
import json

class User:

    def __init__(self, id, interval, locations, enb_signaling_ports):
        self.id = id
        self.interval = interval
        self.locations = locations
        self.enb_signaling_ports = enb_signaling_ports
        self.signaling_connection = False
        self.enb_signaling_sockets = []
        for port in self.enb_signaling_ports:
            self.enb_signaling_sockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

    def __str__(self):
        return f"user id is: {self.id}\nuser interval is: {self.interval}\nuser locations is: {self.locations}"

    def connect(self):
        for i, port in enumerate(self.enb_signaling_ports):
            self.enb_signaling_sockets[i].connect(('127.0.0.1', port))

    def position_announcement(self):

        if not self.signaling_connection:
            self.connect()
            self.signaling_connection = True

        for s in self.enb_signaling_sockets:
            data = {
                "header":{
                    "kind": "Position Announcement"
                },
                "payload":{
                    "uid": self.id,
                    "coordinate": self.locations[0]
                }
            }
            data = json.dumps(data)
            s.sendall(bytes(data, encoding='utf-8'))