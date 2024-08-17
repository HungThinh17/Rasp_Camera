import time
from multiprocessing import Process, Value, Manager

class MyClass:
    def __init__(self, shared_value, shared_dict):
        self.shared_value = shared_value
        self.shared_dict = shared_dict

    def update_values(self):
        self.shared_value.value += 1
        self.shared_dict['hung'] = self.shared_value.value

def worker(shared_value, shared_dict):
    my_instance = MyClass(shared_value, shared_dict)
    while True:
        my_instance.update_values()
        print(f"Worker: Shared Value: {shared_value.value}, Shared Dict: {shared_dict['hung']}")
        time.sleep(2)

if __name__ == '__main__':
    # Create shared objects
    value = Value('i', 0)
    manager = Manager()
    shared_dict = manager.dict({'count': 0})

    # Spawn a process
    p = Process(target=worker, args=(value, shared_dict))
    p.start()

    # Monitor changes in the main thread
    while True:
        print(f"Main: Shared Value: {value.value}, Shared Dict: {shared_dict['hung']}")
        time.sleep(1)

    # Wait for the process to finish
    p.join()
