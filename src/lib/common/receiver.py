import threading
import logging
import socket
from .packet import Packet, HEADER_SIZE, PAYLOAD_SIZE

RECV_TIMEOUT = 0.1

class Receiver(threading.Thread):
    def __init__(self, sock, recv_queue):
        super().__init__()
        self.sock = sock
        self.recv_queue = recv_queue
        self.running = threading.Event()
        self.running.set()

    def run(self):
        logging.debug("Thread Receiver comenzó a ejecutarse")
        self.sock.settimeout(RECV_TIMEOUT)
        while self.running.is_set():
            try:
                data, addr = self.sock.recvfrom(HEADER_SIZE + PAYLOAD_SIZE)
                if not data:
                    continue
                try:
                    packet = Packet.parse(data)
                    self.recv_queue.put((packet, addr))
                except Exception as parse_error:
                    logging.error(f"Error parseando {addr}: {parse_error}")
            except socket.timeout:
                continue
            except Exception as e:
                if self.running.is_set():
                    logging.error(f"Error en Thread Receiver: {e}")
        logging.debug("Thread Receiver detenido")

    def stop(self):
        self.running.clear()
        if self.is_alive():
            self.join()
