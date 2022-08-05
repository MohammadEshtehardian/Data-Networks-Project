import socket
import threading
import json
from ENB import ENB
from MME import MME
from SGW import SGW
from User import User

class Topo:

    def __init__(self, max_entry, enb_file_path, user_file_path, mme_port=65535):
        self.mme = MME(mme_port)
        self.sgw = SGW(max_entry)
        self.enbs = []
        self.add_enbs(enb_file_path, mme_port)
        self.users = []
        self.add_users(user_file_path)


    def add_enbs(self, file_path, mme_port=65535): # this function create enbs from json input file
        file = open(file_path)
        data = json.load(file)
        number_of_enbs = len(data["eNodeBsLocation"])
        for i, coordinate_str in enumerate(data["eNodeBsLocation"]):
            coordinate = tuple(map(int, coordinate_str[1:-1].split(', ')))
            uid = str(int((i+1)*20000/number_of_enbs))
            self.enbs.append(ENB(uid, coordinate, mme_port))

    def add_users(self, file_path): # this function create users from json input file
        file = open(file_path)
        data = json.load(file)
        users = data["users"]
        for user in users:
            user_data = data[user]
            locations = []
            for location in user_data["locations"]:
                locations.append(tuple(map(int, location[1:-1].split(', '))))
            self.users.append(User(user_data["id"], user_data["interval"], locations))

    def send_uid_to_mme(self):
        threads = []
        for enb in self.enbs:
            t = threading.Thread(target=enb.ENB_MME_connection)
            threads.append(t)
        for t in threads:
            t.start()