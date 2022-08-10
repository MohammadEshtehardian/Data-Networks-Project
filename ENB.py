import math
import socket
import json
from threading import Thread, Lock
import logging
import random
import time

class ENB:

    def __init__(self, uid, coordinate, mme_port, sgw_port, t0):
        self.t0 = t0
        self.uid = uid
        self.buffer = []
        self.users = {}
        self.coordinate = coordinate
        self.mme_port = mme_port
        self.mme_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket for connecting to MME
        self.sgw_port = sgw_port
        self.sgw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket for connecting to SGW
        self.lock = Lock()
        self.data_recieved_from_mme = {}
        self.users_sockets = {}
        self.ports = []

    def __str__(self):
        return f"uid is: {self.uid}\ncoordinate is: {self.coordinate}"

    def ENB_MME_connection(self):
        # connecting to MME and send uid to it
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
        # connecting to SGW and send uid to it
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
        # handling position announcement messages
        while True:
            data = str(c.recv(4096), 'utf-8')
            data = json.loads(data)
            if data["header"]["kind"] == "Position Announcement":
                # extract data from message
                id = data["payload"]["id"]
                coordinate = data["payload"]["coordinate"]
                distance = math.sqrt((self.coordinate[0]-coordinate[0])**2+(self.coordinate[1]-coordinate[1])**2)
                self.users[id] = distance
                self.users_sockets[id] = c
                t = data["header"]["time"]
                logging.info(f'eNodeB with uid {self.uid} got position of user with id {id} at time {t}.')
                # send distance of the user to MME
                data = {
                    "header":{
                        "uid": self.uid,
                        "kind": "User Distance"
                    },
                    "payload":{
                        "id": id,
                        "distance": distance,
                        "time": t
                    }
                }
                data = json.dumps(data)
                self.mme_socket.sendall(bytes(data, encoding='utf-8'))
                time.sleep(random.uniform(0.5, 1))
                self.mme_socket.sendall(bytes(data, encoding='utf-8'))
                time.sleep(random.uniform(0, 0.5))
                self.mme_socket.sendall(bytes(data, encoding='utf-8'))
                logging.info(f'Message for announcing position of user with id {id} sends to MME from eNodeB with uid {self.uid}.')

                def recieve():
                    self.lock.acquire()
                    data = str(self.mme_socket.recv(4096), 'utf-8')
                    datas = data.split(';')
                    for data in datas:
                        if data == '':
                            break
                        data = json.loads(data)
                        self.data_recieved_from_mme = data
                        logging.info(f'MME set eNodeB with uid {self.uid} to get data from user with id {data["payload"]["id"]} at time {time.time()-self.t0}')
                    self.lock.release()
                    return

                def send():
                    self.lock.acquire()
                    data = self.data_recieved_from_mme
                    id = data["payload"]["id"]
                    time = data["payload"]["time"]
                    data = {
                        "header": {
                            "kind": "User-eNodeB Connection"
                        },
                        "payload": {
                            "uid": self.uid,
                            "time": time
                        }
                    }
                    data = json.dumps(data)
                    Thread(target=self.start_server, args=(int(self.uid)+1,)).start()
                    self.users_sockets[id].sendall(bytes(data, 'utf-8'))
                    logging.info(f'eNodeB with uid {self.uid} request for construction of data channel to user with id {id}.')
                    self.lock.release()
                Thread(target=recieve).start()
                Thread(target=send).start()

            

    def start_server(self, port=-1):
        # start ENB server for connecting to users
        if port == -1:
            port = int(self.uid)
        if port not in self.ports:
            self.ports.append(port)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', port))
            s.listen()
            logging.critical(f'Server of eNodeB with uid {self.uid} started on port {port}.')
            while True:
                c, addr = s.accept()
                if port == int(self.uid):
                    Thread(target=self.position_announcement, args=(c,)).start()
            
