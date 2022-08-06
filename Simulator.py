from Topology import Topo
import threading
import time

class Simulation:

    def __init__(self, T, dt, max_entry, enb_file_path, user_file_path):
        topo = Topo(max_entry, enb_file_path, user_file_path)
        threading.Thread(target=topo.send_uid_to_mme_sgw).start()
        events = []
        for user in topo.users:
            e = threading.Event()
            threading.Thread(target=user.connect, args=(e,)).start()
            events.append(e)
        t = 0
        while t <= T:
            for i, user in enumerate(topo.users):
                threading.Thread(target=user.position_announcement, args=(t, events[i])).start()
            t += dt


if __name__ == '__main__':
    Simulation(1e4, 1, 1, 'ENB.json', 'Users1.json')