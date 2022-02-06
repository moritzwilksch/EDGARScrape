# Bufferrs data before writing it. Useful for speed?

from queue import Queue
from threading import Thread
import time, random

class BufferedDBWriter:
    def __init__(self):
        self.buffer = []
        self.incoming_data = Queue()
        self.start_worker()

    def write(self, data):
        self.incoming_data.put(data)

    def worker(self):
        while True:
            if len(self.buffer) == 5:
                print(f"[WRITING] {self.buffer}")
                self.buffer = []
            
            data = self.incoming_data.get()
            if data == "<ENDOFQUEUE>":
                break
            self.buffer.append(data)

    def start_worker(self):
        Thread(target=self.worker).start()
    
    def close(self):
        self.incoming_data.put("<ENDOFQUEUE>")


bw = BufferedDBWriter()
for i in range(100):
    bw.write(i)
    time.sleep(random.randrange(1, 50)/100)
bw.close()