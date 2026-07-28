import socket
import logging
from .protocol import Protocol
from .packet import Packet, HEADER_SIZE, PAYLOAD_SIZE, DATA, ACK, FIN

WINDOW_SIZE = 10

class GoBackNProtocol(Protocol):

    def send_file(self, file_path):
        chunks = self._read_chunks(file_path)
        total = len(chunks)
        base = 0
        next_seq = 0

        while base < total:
            if self.check_interruption(next_seq):
                return
            next_seq = self._send_window(chunks, base, next_seq, total)
            try:
                base = self._wait_for_acks(base, next_seq)
                if base is None:
                    return 
            except socket.timeout:
                for seq in range(base, next_seq):
                    packet = Packet.build(DATA, seq, chunks[seq])
                    self._send(packet)
                    logging.debug(f"Timeout: Reenviado paquete DATA con seq {seq} a {self.peer_addr}")

        fin_seq = next_seq
        self.send_fin(fin_seq)
    
    def _send_window(self, chunks, base, next_seq, total):
        while next_seq < total and next_seq < base + WINDOW_SIZE:
            packet = Packet.build(DATA, next_seq, chunks[next_seq])
            self._send(packet)
            logging.debug(f"Enviado paquete DATA con seq {next_seq} a {self.peer_addr}")
            next_seq += 1
        return next_seq
    
    def _wait_for_acks(self, base, next_seq):
        pkt_data, _ = self._recv()
        ack_type, ack_seq, _ = pkt_data
        
        if ack_type == ACK and base <= ack_seq < next_seq:
            logging.debug(f"Recibido ACK para seq {ack_seq} de {self.peer_addr}")
            return ack_seq + 1
        elif ack_type == FIN:
            logging.info(f"Recibido FIN con seq {ack_seq} durante envío, finalizando transferencia")
            self._send(Packet.build(ACK, ack_seq))  
            return None
        return base
    
    def recv_file(self, dest_path):
        expected_seq = 0
        last_ack_sent = None
        with open(dest_path, 'wb') as f:
            while True:
                if self.check_interruption(expected_seq):
                    return

                try:
                    pkt_data, addr = self._recv()
                    self.peer_addr = addr
                    pkt_type, seq_num, payload = pkt_data

                    if pkt_type == DATA:
                        last_ack_sent, expected_seq = self._handle_data(f, seq_num, expected_seq, payload, last_ack_sent)
                    elif pkt_type == FIN:
                        self._handle_fin(seq_num)
                        break
                except socket.timeout:
                    continue

    def _handle_data(self, f, seq_num, expected_seq, payload, last_ack_sent):
        if seq_num == expected_seq:
            f.write(payload)
            ack = Packet.build(ACK, seq_num)
            self._send(ack)
            logging.debug(f"Recibido paquete DATA con seq {seq_num} de {self.peer_addr}, enviado ACK")
            return seq_num, expected_seq + 1
        else:
            logging.debug(f"Recibido paquete DATA fuera de orden con seq {seq_num} de {self.peer_addr}, esperado {expected_seq}. Reenviando ACK del último paquete correcto.")
            if last_ack_sent is not None:
                ack = Packet.build(ACK, last_ack_sent)
                self._send(ack)
                logging.debug(f"Reenviado ACK para seq {last_ack_sent} a {self.peer_addr}")
            return last_ack_sent, expected_seq

    def _handle_fin(self, seq_num):
        logging.info(f"Recibido FIN con seq {seq_num} de {self.peer_addr}")
        ack = Packet.build(ACK, seq_num)
        self._send(ack)
        

    