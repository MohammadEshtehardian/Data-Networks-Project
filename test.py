from Topology import Topo
import threading

t1 = Topo(100, "ENB.json", "Users1.json")
thr1 = threading.Thread(target=t1.mme.start_server)
thr2 = threading.Thread(target=t1.sgw.start_server)
thr3 = threading.Thread(target=t1.send_uid_to_mme_sgw)
thr4 = threading.Thread(target=t1.connect_sgw_mme)
thr1.start()
thr2.start()
thr3.start()
thr4.start()