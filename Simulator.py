from Topology import Topo
import threading
import time
import logging
import sys
import json
import os

class Simulation:

    def __init__(self, T, max_entry, enb_file_path, user_file_path, scenario_file_path):
        t0 = time.time()
        topo = Topo(max_entry, enb_file_path, user_file_path, scenario_file_path, t0)
        topo.add_scenario("scenarios.json")
        threading.Thread(target=topo.connect_sgw_mme).start()
        threading.Thread(target=topo.send_uid_to_mme_sgw).start()
        events = []
        for user in topo.users:
            e = threading.Event()
            threading.Thread(target=user.connect, args=(e,)).start()
            events.append(e)
        while time.time() - t0 <= T:
            for i, user in enumerate(topo.users):
                threading.Thread(target=user.position_announcement, args=(time.time()-t0, events[i])).start()
            time.sleep(0.5)

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1]=='INFO':
        logging.basicConfig(level = logging.INFO,
                            format = '%(levelname)s:%(message)s')
    elif len(sys.argv) == 3 and sys.argv[1]=='INFO':
        os.remove(sys.argv[2])
        logging.basicConfig(filename = sys.argv[2],
                            level = logging.INFO,
                            format = '%(levelname)s:%(message)s')
    Simulation(20, 100, 'ENB.json', 'Users1.json', 'scenarios.json')