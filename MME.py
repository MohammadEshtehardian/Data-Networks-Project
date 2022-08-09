import socket
import json
from textwrap import indent
from threading import Thread, Lock
import logging
from operator import itemgetter

class MME:

    def __init__(self, port, sgw_port):
        self.enb_uids = []
        self.port = port
        self.sgw_port = sgw_port
        self.sgw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket for connecting to SGW
        self.messages = [] # buffer distances that recieved from ENBs

    def __str__(self):
        return f"ENBs are: {self.uids}"

    def ENB_MME_connection(self, c):
        # handling messages for connections from ENBs
        while True:
            data = str(c.recv(4096), 'utf-8')
            data = json.loads(data)
            if data["header"]["kind"] == "eNodeB-MME Connection":
                uid = data["payload"]["uid"]
                self.enb_uids.append(uid)
                logging.info(f'MME added eNodeB with uid {uid} to its eNodebs list.')

    def user_distance(self, c, s):
        # handling messages for announcing distance of user
        while True:
            data = str(c.recv(4096), 'utf-8')
            data = json.loads(data)
            if data["header"]["kind"] == "User Distance":
                uid = data["header"]["uid"]
                id = data["payload"]["id"]
                distance = data["payload"]["distance"]
                time = data["payload"]["time"]
                self.messages.append({
                    "id": id,
                    "time": time,
                    "uid": uid,
                    "distance": distance
                })
                logging.info(f'Distance of user with id {id} at time {time} from eNodeB with uid {uid} recieved.')
                

    def start_server(self):
        # starting server 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.port))
        s.listen()
        logging.critical(f'Server of MME started on port {self.port}.')
        while True:
            c, addr = s.accept()
            Thread(target=self.ENB_MME_connection, args=(c,)).start()
            Thread(target=self.user_distance, args=(c, s)).start()

    def connect_sgw(self):
        # connect to SGW
        try:
            self.sgw_socket.connect(('127.0.0.1', self.sgw_port))
            logging.critical('MME connected to SGW.')
        except:
            logging.error('MME cannot connect to SGW!!!')

            

