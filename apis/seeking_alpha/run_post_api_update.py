from update_symbol_profile import update_symbol_profile
import threading


# if __name__ == "__main__":
#     mdb_holding_history()
#     mdb_sa_history()
#     update_symbol_profile()
#     update_symbol_info()
if __name__ == "__main__":
    # Create the threads
    t1 = threading.Thread(target=mdb_holding_history)
    t2 = threading.Thread(target=mdb_sa_history)
    t3 = threading.Thread(target=update_symbol_profile)
#    t4 = threading.Thread(target=update_symbol_info)

    t1.start()
    t2.start()
    t3.start()
#    t4.start()
