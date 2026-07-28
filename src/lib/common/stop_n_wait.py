import logging
import socket
from .protocol import Protocol
from .packet import Packet, HEADER_SIZE, PAYLOAD_SIZE, DATA, ACK, FIN

class StopNWaitProtocol(Protocol):
    def send_file(self, file_path):
        seq_num = 0
        with open(file_path, 'rb') as f:
            while True:
                if self.check_interruption(seq_num):
                    return

                chunk = f.read(PAYLOAD_SIZE)
                logging.debug(f"Leído del archivo {len(chunk)} bytes para enviar")
                if not chunk:
                    break
                if not self._send_chunk_conf(chunk, seq_num):
                    return
                seq_num = 1 - seq_num

        logging.info(f"Archivo {file_path} enviado completamente, enviando FIN")                
        self.send_fin(seq_num)

    def _send_chunk_conf(self, chunk, seq_num):
        packet = Packet.build(DATA, seq_num, chunk)
        while True: 
            if self.check_interruption(seq_num):
                return
            self._send(packet)
            logging.debug(f"DATA enviado a {self.peer_addr} con seq_num={seq_num}, esperando ACK...")
            try:
                pkt_data, _ = self._recv()
                ack_type, ack_seq_num, _ = pkt_data
                if ack_type == ACK and ack_seq_num == seq_num:
                    logging.debug(f"ACK recibido de {self.peer_addr} con seq_num={ack_seq_num} correcto, continuando con el siguiente chunk")
                    return True
                elif ack_type == FIN:
                    logging.info(f"Recibido FIN con seq_num={ack_seq_num} de {self.peer_addr} durante envío, finalizando transferencia")
                    ack = Packet.build(ACK, seq_num)
                    self._send(ack) 
                    return False
            except socket.timeout:
                logging.info(f"Timeout esperando ACK de {self.peer_addr} para seq_num={seq_num}, reintentando...")
                continue
    
    def recv_file(self, dest_path):
        expected_seq_num = 0
        with open(dest_path, 'wb') as f:
            while True:
                if self.check_interruption(expected_seq_num):
                    return

                try:
                    pkt_data, addr = self._recv()
                    self.peer_addr = addr
                    packet_type, seq_num, playload = pkt_data
                    if packet_type == DATA:  
                        expected_seq_num = self._handle_data(f, seq_num, expected_seq_num, playload)
                    elif packet_type == FIN:
                        self._handle_fin(seq_num)
                        break
                except socket.timeout:
                    continue

    def _handle_data(self, f, seq_num, expected_seq_num, payload):
        if seq_num == expected_seq_num:
            logging.info(f"DATA recibido de {self.peer_addr} con seq_num={seq_num}, escribiendo en archivo")
            logging.debug(f"Payload del DATA: {len(payload)} bytes")
            f.write(payload)
            expected_seq_num = 1 - expected_seq_num
        else:
            logging.info(f"Paquete fuera de orden, enviando ack duplicado para seq_num={1 - expected_seq_num}")
        ack_packet = Packet.build(ACK, seq_num)
        self._send(ack_packet)
        logging.debug(f"ACK enviado a {self.peer_addr} con seq_num={seq_num}")
        return expected_seq_num
    
    def _handle_fin(self, seq_num):
        logging.info(f"Recibido FIN con seq_num={seq_num} de {self.peer_addr}")
        ack = Packet.build(ACK, seq_num)
        self._send(ack)

