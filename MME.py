import socket
import json
from ENB import ENB

class MME:

    def __init__(self, port):
        self.enbs = []
        self.port = port

    def start_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.port))
        s.listen()
        while True:
            c, addr = s.accept()    
            data = str(c.recv(4096), 'utf-8')
            data = json.loads(data)
            if data["header"]["kind"] == "eNodeB-MME Connection":
                enb = ENB(data["payload"]["uid"], None)
                self.enbs.append(enb)
            for enb in self.enbs:
                print(enb)
            print()
            print()
                

            

