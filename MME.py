import random
import socket
import json
from textwrap import indent
from threading import Thread, Lock
import logging
import select
from operator import itemgetter
from time import sleep

class MME:

    def __init__(self, port, sgw_port, t0):
        self.enb_uids = {}
        self.port = port
        self.sgw_port = sgw_port
        self.t0 = t0
        self.sgw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket for connecting to SGW
        self.messages = {} # buffer distances that recieved from ENBs
        self.served_times = []
        self.table = {}

    def __str__(self):
        return f"ENBs are: {self.uids}"

    def ENB_MME_connection(self, c):
        # handling messages for connections from ENBs
        while True:
            data = str(c.recv(4096), 'utf-8')
            datas = data.split(';')
            for data in datas:
                if data != '':
                    data = json.loads(data)
                    if data["header"]["kind"] == "ASK Route":
                        print(data)
                    if data["header"]["kind"] == "eNodeB-MME Connection":
                        uid = data["payload"]["uid"]
                        self.enb_uids[uid] = c
                        logging.info(f'MME added eNodeB with uid {uid} to its eNodebs list.')
                    elif data["header"]["kind"] == "User Distance":
                        uid = data["header"]["uid"]
                        id = data["payload"]["id"]
                        distance = data["payload"]["distance"]
                        time = data["payload"]["time"]
                        if id in list(self.messages.keys()):
                            times = self.messages[id]
                            if time in list(times.keys()):
                                self.messages[id][time][uid] = distance
                            else:
                                self.messages[id][time] = {uid: distance}
                        else:
                            self.messages[id] = {
                                time:{
                                    uid: distance
                                }
                            }
                        for id in list(self.messages.keys()):
                            for time in list(self.messages[id].keys()):
                                if len(self.messages[id][time]) == len(self.enb_uids) and {id: time} not in self.served_times:
                                    self.served_times.append({id: time})
                                    distance = 1e10
                                    min_dist_uid = None
                                    for uid in list(self.messages[id][time].keys()):
                                        if self.messages[id][time][uid] < distance:
                                            distance = self.messages[id][time][uid]
                                            min_dist_uid = uid 
                                    data = {
                                        "header": {
                                        "kind": "User-eNodeB registeration"
                                        },
                                        "payload": {
                                            "time": time,
                                            "uid": min_dist_uid,
                                            "id": id
                                        }
                                    }
                                    self.table[id] = min_dist_uid
                                    data = json.dumps(data) + ';'
                                    self.enb_uids[min_dist_uid].sendall(bytes(data, encoding='utf-8'))
                                    self.messages[id].pop(time)
                                    
                        logging.info(f'Distance of user with id {id} at time {time} from eNodeB with uid {uid} recieved.')

    # def user_distance(self, c, s):
    #     # handling messages for announcing distance of user
    #     while True:
    #         data = str(c.recv(4096), 'utf-8')
    #         data = json.loads(data)
            # if data["header"]["kind"] == "User Distance":
            #     uid = data["header"]["uid"]
            #     id = data["payload"]["id"]
            #     distance = data["payload"]["distance"]
            #     time = data["payload"]["time"]
            #     if id in list(self.messages.keys()):
            #         times = self.messages[id]
            #         if time in list(times.keys()):
            #             self.messages[id][time][uid] = distance
            #         else:
            #             self.messages[id][time] = {uid: distance}
            #     else:
            #         self.messages[id] = {
            #             time:{
            #                 uid: distance
            #             }
            #         }
            #     for id in list(self.messages.keys()):
            #         for time in list(self.messages[id].keys()):
            #             if len(self.messages[id][time]) == len(self.enb_uids) and {id: time} not in self.served_times:
            #                 self.served_times.append({id: time})
            #                 distance = 1e10
            #                 min_dist_uid = None
            #                 for uid in list(self.messages[id][time].keys()):
            #                     if self.messages[id][time][uid] < distance:
            #                         distance = self.messages[id][time][uid]
            #                         min_dist_uid = uid 
            #                 data = {
            #                     "header": {
            #                     "kind": "User-eNodeB registeration"
            #                     },
            #                     "payload": {
            #                         "time": time,
            #                         "uid": min_dist_uid,
            #                         "id": id
            #                     }
            #                 }
            #                 self.table[id] = min_dist_uid
            #                 data = json.dumps(data) + ';'
            #                 self.enb_uids[min_dist_uid].sendall(bytes(data, encoding='utf-8'))
            #                 self.messages[id].pop(time)
                            
            #     logging.info(f'Distance of user with id {id} at time {time} from eNodeB with uid {uid} recieved.')

    # def ask_route(self, c):
    #     while True:
    #         data = str(c.recv(4096), 'utf-8')
    #         data = json.loads(data)
    #         print(data)
    #         if data["header"]["kind"] == "Bye":
    #             print(data)
                # if data["payload"]["dest"] not in list(self.routing_table.keys()):
                #     ask_route = {
                #         "header": {
                #             "kind": "ASK Route"
                #         },
                #         "payload": {
                #             "dest":  data["payload"]["dest"]
                #         }
                #     }
                #     ask_route = json.dumps(ask_route)
                #     self.mme_socket.sendall(bytes(ask_route, 'utf-8'))
                

    def start_server(self):
        # starting server 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.port))
        s.listen()
        logging.critical(f'Server of MME started on port {self.port}.')
        while True:
            c, addr = s.accept()
            Thread(target=self.ENB_MME_connection, args=(c,)).start()
            # Thread(target=self.user_distance, args=(c, s)).start()
            # Thread(target=self.ask_route, args=(c,)).start()

    def connect_sgw(self):
        # connect to SGW
        try:
            self.sgw_socket.connect(('127.0.0.1', self.sgw_port))
            logging.critical('MME connected to SGW.')
        except:
            logging.error('MME cannot connect to SGW!!!')

            

