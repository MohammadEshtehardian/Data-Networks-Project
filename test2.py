import json
import socket
from ENB import ENB

s = socket.socket()
s.connect(('127.0.0.1', 65535))
data = {"header": {"kind": "test"}, "payload": "This is for test."}
data = json.dumps(data)
s.sendall(bytes(data, encoding='utf-8'))

s1 = socket.socket()
s1.connect(('127.0.0.1', 65000))
data = {"header": {"kind": "test"}, "payload": "This is for test."}
data = json.dumps(data)
s.sendall(bytes(data, encoding='utf-8'))