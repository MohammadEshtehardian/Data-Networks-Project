import socket
import json
from threading import Thread
import logging

class ENB:

    def __init__(self, uid, coordinate, mme_port, sgw_port):
        self.uid = uid
        self.buffer = []
        self.users = {}
        self.coordinate = coordinate
        self.mme_port = mme_port
        self.mme_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sgw_port = sgw_port
        self.sgw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __str__(self):
        return f"uid is: {self.uid}\ncoordinate is: {self.coordinate}"

    def ENB_MME_connection(self):
        self.mme_socket.connect(('127.0.0.1', self.mme_port))
        data = {
            "header":{
                "kind": "eNodeB-MME Connection"
            },
            "payload":{
                "uid": self.uid
            }
        }
        data = json.dumps(data)
        self.mme_socket.sendall(bytes(data, encoding='utf-8'))
        logging.critical(f'eNodeB with UID {self.uid} connected to MME.')

    def ENB_SGW_connection(self):
        self.sgw_socket.connect(('127.0.0.1', self.sgw_port))
        data = {
            "header":{
                "kind": "eNodeB-SGW Connection"
            },
            "payload":{
                "uid": self.uid
            }
        }
        data = json.dumps(data)
        self.sgw_socket.sendall(bytes(data, encoding='utf-8'))
        logging.critical(f'eNodeB with UID {self.uid} connected to SGW.')

    def position_announcement(self, c):
        while True:
            data = str(c.recv(4096), 'utf-8')
            data = json.loads(data)
            if data["header"]["kind"] == "Position Announcement":
                uid = data["payload"]["uid"]
                coordinate = data["payload"]["coordinate"]
                self.users[uid] = coordinate
                time = data["header"]["time"]
                logging.info(f'eNodeB with uid {self.uid} got position of user with id {uid} at time {time}.')
            

    def start_server(self):
        port = int(self.uid)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', port))
        s.listen()
        logging.critical(f'Server of eNodeB with uid {self.uid} started on port {port}.')
        while True:
            c, addr = s.accept()
            Thread(target=self.position_announcement, args=(c,)).start()
            
