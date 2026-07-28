import logging
import socket
import queue
from .packet import Packet, DATA, ACK, SYN, FIN, PAYLOAD_SIZE
from .sender import Sender
from .receiver import Receiver

TIMEOUT = 0.05
MAX_FIN_RETRIES = 5

class Protocol:
    def __init__(self, sock, peer_addr):
        self.sock = sock
        self.peer_addr = peer_addr
        self.send_queue = queue.Queue()
        self.recv_queue = queue.Queue()
        self.sender = Sender(self.sock, self.send_queue)
        self.receiver = Receiver(self.sock, self.recv_queue)
        self.sender.start()
        self.receiver.start()
        self.alive = True

    def _send(self, packet, addr=None):
        target_addr = addr if addr else self.peer_addr
        self.send_queue.put((packet, target_addr))

    def _recv(self, timeout=None):
        try:
            return self.recv_queue.get(timeout=timeout if timeout else TIMEOUT)
        except queue.Empty:
            raise socket.timeout

    def request_stop(self):
        self.alive = False

    def stop(self):
        self.alive = False
        self.sender.stop()
        self.receiver.stop()
        self.receiver.join()
        self.sender.join()

    def send_syn(self, metadata=b''):
        syn = Packet.build(SYN, 0, metadata)
        while self.alive:
            self._send(syn)
            logging.debug(f"SYN enviado a {self.peer_addr} con metadata")
            try:
                pkt_data, addr = self._recv()
                pkt_type, _, _ = pkt_data
                if pkt_type == ACK:
                    logging.debug(f"SYN-ACK recibido de {addr}")
                    self.peer_addr = addr
                    ack = Packet.build(ACK, 0)
                    self._send(ack)
                    logging.debug(f"ACK de confirmación 3WHS enviado a {self.peer_addr}")
                    break
            except socket.timeout:
                logging.debug(f"Timeout esperando SYN-ACK de {self.peer_addr}, reintentando SYN...")
                continue

    def recv_syn(self):
        while self.alive:
            ack = Packet.build(ACK, 0)
            self._send(ack)
            logging.debug(f"SYN-ACK enviado a {self.peer_addr} en respuesta al SYN")
            try:
                pkt_data, _ = self._recv(timeout=1.0)
                pkt_type_ack, _, _ = pkt_data
                if pkt_type_ack == ACK or pkt_type_ack == DATA:
                    logging.debug(f"ACK recibido de {self.peer_addr}")
                    return  # Handshake exitoso
                elif pkt_type_ack == SYN:
                    # Si recibe un SYN de nuevo, es que nuestro ACK se perdió. Vuelve a repetir el proceso.
                    continue
            except socket.timeout:
                continue

    def send_file(self, file_path):
        pass

    def recv_file(self, dest_path):
        pass

    def send_fin(self, fin_seq):
        fin = Packet.build(FIN, fin_seq)
        logging.info(f"Enviando FIN con seq {fin_seq} a {self.peer_addr}")

        for _ in range(MAX_FIN_RETRIES):
            self._send(fin)
            try:
                pkt_data, _ = self._recv()
                ack_type, ack_seq, _ = pkt_data
                if ack_type == ACK and ack_seq == fin_seq:
                    logging.info(f'Recibiendo ACK de FIN. Cierre de conexión confirmado por {self.peer_addr}')
                    break
            except socket.timeout:
                logging.debug(f"Timeout esperando ACK de FIN de {self.peer_addr}, reintentando FIN...")
                continue

    def check_interruption(self, next_seq):
        if not self.alive:
            logging.info(f"Interrupción detectada para {self.peer_addr}")
            self.send_fin(next_seq)
            return True
        return False
    
    def _read_chunks(self, file_path):
        chunks = []
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(PAYLOAD_SIZE)
                if not chunk:
                    break
                chunks.append(chunk)
        return chunks
