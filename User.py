from math import floor
from prefixed import Float
import socket
import threading
import json
import logging
import time

class User:

    def __init__(self, id, interval, locations, enb_signaling_ports, t0):
        self.t0 = t0
        self.id = id
        self.interval = interval
        self.locations = locations
        self.enb_signaling_ports = enb_signaling_ports
        self.enb_signaling_sockets = []
        self.announced_locations = []
        self.lock = threading.Lock()
        for port in self.enb_signaling_ports:
            self.enb_signaling_sockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.enb_data_sockets = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.enb_conncted = ''

    def __str__(self):
        return f"user id is: {self.id}\nuser interval is: {self.interval}\nuser locations is: {self.locations}"

    def connect(self, e):
        for i, port in enumerate(self.enb_signaling_ports):
            self.enb_signaling_sockets[i].connect(('127.0.0.1', port))
            logging.critical(f'User with id {self.id} connected to eNodeB on port {port}.')
        e.set()

    def run_scenario(self, scenario):
        while True:
            if time.time() - self.t0 >= Float(scenario["when"][:-1]):
                pass

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
                        "id": self.id,
                        "coordinate": self.locations[ind]
                    }
                }
                data = json.dumps(data)
                s.sendall(bytes(data + ';', encoding='utf-8'))

                def get_data_channel_message():
                    data = str(s.recv(4096), 'utf-8')
                    data = json.loads(data)
                    if data["header"]["kind"] == "User-eNodeB Connection" and not self.enb_conncted == data["payload"]["uid"]:
                        self.enb_conncted = data["payload"]["uid"]
                        for j in range(len(self.enb_signaling_ports)):
                            if int(data["payload"]["uid"]) == self.enb_signaling_ports[j]:
                                self.enb_data_sockets.connect(('127.0.0.1', self.enb_signaling_ports[j]+1))

                threading.Thread(target=get_data_channel_message).start()

        self.lock.release()