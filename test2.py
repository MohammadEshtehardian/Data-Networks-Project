import socket
from ENB import ENB

e = ENB(100, (1, 2), 1000, 2000, 3000, 9000)
e.connect_sgw()