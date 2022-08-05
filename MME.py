import socket
import json

class MME:

    def __init__(self, port, sgw_port):
        self.enb_uids = []
        self.port = port
        self.sgw_port = sgw_port
        self.sgw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __str__(self):
        return f"ENBs are: {self.uids}"

    def start_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.port))
        s.listen()
        while True:
            c, addr = s.accept()
            data = str(c.recv(4096), 'utf-8')
            data = json.loads(data)
            if data["header"]["kind"] == "eNodeB-MME Connection":
                uid = data["payload"]["uid"]
                self.enb_uids.append(uid)

    def connect_sgw(self):
        self.sgw_socket.connect(('127.0.0.1', self.sgw_port))

            

