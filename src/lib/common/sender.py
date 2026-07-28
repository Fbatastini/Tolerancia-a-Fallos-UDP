import threading
import queue
import logging

TIMEOUT_SENDER = 0.1

class Sender(threading.Thread):
    def __init__(self, sock, send_queue):
        super().__init__()
        self.sock = sock
        self.queue = send_queue
        self.running = threading.Event()
        self.running.set()

    def run(self):
        logging.debug("Thread Sender comenzó a ejecutarse")
        while self.running.is_set():
            try:
                packet, addr = self.queue.get(timeout=TIMEOUT_SENDER)
                self.sock.sendto(packet, addr)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                if self.running.is_set():
                    logging.error(f"Error en Thread Sender: {e}")
        logging.debug("Thread Sender detenido")

    def stop(self):
        self.running.clear()
        if self.is_alive():
            self.join()
