import socket
import json

class ENB:

    def __init__(self, uid, coordinate, mme_port=65535):
        self.uid = uid
        self.buffer = []
        self.coordinate = coordinate
        self.mme_port = mme_port

    def __str__(self):
        return f"uid is: {self.uid}\ncoordinate is: {self.coordinate}"

    def ENB_MME_connection(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', self.mme_port))
        data = {
            "header":{
                "kind": "eNodeB-MME Connection"
            },
            "payload":{
                "uid": self.uid
            }
        }
        data = json.dumps(data)
        s.sendall(bytes(data, encoding='utf-8'))