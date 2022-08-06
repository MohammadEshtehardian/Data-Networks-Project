import socket
import threading
import json
from prefixed import Float
from ENB import ENB
from MME import MME
from SGW import SGW
from User import User

class Topo:

    def __init__(self, max_entry, enb_file_path, user_file_path, mme_port=65535, sgw_port=65000):
        self.mme = MME(mme_port, sgw_port)
        self.sgw = SGW(max_entry, sgw_port, mme_port)
        self.enbs = []
        self.enb_signaling_ports = []
        self.add_enbs(enb_file_path, mme_port, sgw_port)
        self.users = []
        self.add_users(user_file_path)
        self.start_servers()


    def add_enbs(self, file_path, mme_port, sgw_port): # this function create enbs from json input file
        file = open(file_path)
        data = json.load(file)
        number_of_enbs = len(data["eNodeBsLocation"])
        for i, coordinate_str in enumerate(data["eNodeBsLocation"]):
            coordinate = tuple(map(int, coordinate_str[1:-1].split(', ')))
            uid = str(int((i+1)*20000/number_of_enbs))
            self.enb_signaling_ports.append(int(uid))
            self.enbs.append(ENB(uid, coordinate, mme_port, sgw_port))

    def add_users(self, file_path): # this function create users from json input file
        file = open(file_path)
        data = json.load(file)
        users = data["users"]
        for user in users:
            user_data = data[user]
            locations = []
            for location in user_data["locations"]:
                locations.append(tuple(map(int, location[1:-1].split(', '))))
            self.users.append(User(user_data["id"], Float(user_data["interval"][:-1]), locations, self.enb_signaling_ports))

    def start_servers(self): # this function starts servers on ENBs, MME and SGW
        t1 = threading.Thread(target=self.mme.start_server)
        t2 = threading.Thread(target=self.sgw.start_server)
        t1.start()
        t2.start()
        for enb in self.enbs:
            t = threading.Thread(target=enb.start_server)
            t.start()


    def send_uid_to_mme_sgw(self): # this function sends uids of the ENBs to MME and SGW
        threads = []
        for enb in self.enbs:
            t1 = threading.Thread(target=enb.ENB_MME_connection)
            t2 = threading.Thread(target=enb.ENB_SGW_connection)
            threads.append(t1)
            threads.append(t2)
        for t in threads:
            t.start()

    def connect_sgw_mme(self): # this function connects sgw to mme
        t1 = threading.Thread(target=self.mme.connect_sgw)
        t2 = threading.Thread(target=self.sgw.connect_mme)
        t1.start()
        t2.start()