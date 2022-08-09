from math import floor
import socket
import threading
import json
import logging

class User:

    def __init__(self, id, interval, locations, enb_signaling_ports):
        self.id = id
        self.interval = interval
        self.locations = locations
        self.enb_signaling_ports = enb_signaling_ports
        self.enb_signaling_sockets = []
        self.announced_locations = []
        self.lock = threading.Lock()
        for port in self.enb_signaling_ports:
            self.enb_signaling_sockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

    def __str__(self):
        return f"user id is: {self.id}\nuser interval is: {self.interval}\nuser locations is: {self.locations}"

    def connect(self, e):
        for i, port in enumerate(self.enb_signaling_ports):
            self.enb_signaling_sockets[i].connect(('127.0.0.1', port))
            logging.critical(f'User with id {self.id} connected to eNodeB on port {port}.')
        e.set()

    def position_announcement(self, time, e):
        e.wait()
        self.lock.acquire()
        ind = floor(time/self.interval) # index of the location that should be announced
        if not ind >= len(self.locations) and ind not in self.announced_locations:
            self.announced_locations.append(ind)
            for s in self.enb_signaling_sockets:
                data = {
                    "header":{
                        "kind": "Position Announcement",
                        "time": time
                    },
                    "payload":{
                        "uid": self.id,
                        "coordinate": self.locations[ind]
                    }
                }
                data = json.dumps(data)
                s.sendall(bytes(data, encoding='utf-8'))
        self.lock.release()