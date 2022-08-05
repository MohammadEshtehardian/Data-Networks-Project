from Topology import Topo
import threading

t1 = Topo(100, "ENB.json", "Users1.json")
thr1 = threading.Thread(target=t1.start_servers)
thr2 = threading.Thread(target=t1.send_uid_to_mme_sgw)
thr3 = threading.Thread(target=t1.users[0].position_announcement)
thr1.start()
thr2.start()
thr3.start()