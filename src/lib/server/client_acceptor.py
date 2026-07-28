import logging
import socket
import threading
from ..common.packet import Packet, HEADER_SIZE, PAYLOAD_SIZE, SYN
from .client_handler import ClientHandler

class ClientAcceptor(threading.Thread):
    def __init__(self, host, port, dir):
        super().__init__()
        self.host = host
        self.port = port
        self.dir = dir
        self.acceptor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.acceptor_socket.bind((self.host, self.port))
        self.clients = []
        self.socket_alive = True
    
    def run(self):
        while self.socket_alive:
            try:
                packet, addr = self.acceptor_socket.recvfrom(HEADER_SIZE + PAYLOAD_SIZE)
                pkt_type, _, data = Packet.parse(packet)
                if pkt_type == SYN:
                    logging.info(f"Received SYN from {addr}")
                    handler = ClientHandler(addr, self.dir, data)
                    self.reap()
                    self.clients.append(handler)
                    handler.start()
            except OSError:
                if not self.socket_alive:
                    break
            except socket.timeout:
                continue
        self.clear()

    def reap(self):
        alive = []
        for handler in self.clients:
            if handler.is_alive():
                alive.append(handler)
            else:
                handler.join()
        self.clients = alive
    
    def clear(self):
        for handler in self.clients:
            handler.stop()
            handler.join()
        self.clients.clear()
        self.acceptor_socket.close()
        self.socket_alive = False
    
    def stop(self):
        self.socket_alive = False
        for handler in self.clients:
            handler.stop()
        try:
            self.acceptor_socket.close() 
        except Exception:
            pass