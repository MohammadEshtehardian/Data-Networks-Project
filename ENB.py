import socket
import json

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

    def start_server(self):
        port = int(self.uid)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', port))
        s.listen()
        while True:
            c, addr = s.accept()
            print("Connection from ", addr)
            data = str(c.recv(4096), 'utf-8')
            data = json.loads(data)
            if data["header"]["kind"] == "Position Announcement":
                uid = data["payload"]["uid"]
                coordinate = data["payload"]["coordinate"]
                if uid not in self.users.keys():
                    self.users[uid] = coordinate
                print(self.users)
                
