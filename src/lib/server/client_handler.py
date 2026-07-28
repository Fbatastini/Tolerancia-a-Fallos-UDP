import logging
import socket
import threading
from lib.common.protocol import Protocol
import lib.common.go_back_n as gbn
import lib.common.stop_n_wait as snw
import os
from lib.common.packet import Packet, DATA



class ClientHandler(threading.Thread): 
    def __init__(self, peer_addr, dir, data):
        super().__init__()
        self.peer_addr = peer_addr
        self.dir = dir
        self.data = data

        self.own_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.own_socket.bind(('0.0.0.0', 0)) 

        self.protocol = None

    def run(self):
        try:
            operation, filename, protocol_name = self._init_process()
            if not operation:
                return
            path = f"{self.dir}/{filename}"

            if not self._init_protocol(protocol_name):
                return

            self.protocol.recv_syn()
            self._execute_operation(operation, path)

        except Exception as e:
            logging.error(f"Error en el handler para {self.peer_addr}: {e}")
        finally:
            if self.protocol:
                self.protocol.stop()
            self.own_socket.close()

    def _init_process(self):
        decoded_data = self.data.decode().split('|')
        if len(decoded_data) != 3:
            logging.error(f"Error: Formato de metadata inválido de {self.peer_addr}")
            packet_error = Packet.build(DATA, 0, b"ERROR|BAD_METADATA")
            self.own_socket.sendto(packet_error, self.peer_addr)
            return None, None, None

        operation, filename, protocol_name = decoded_data
        logging.debug(f"Metadata recibida de {self.peer_addr}: Operación={operation}, Filename={filename}, Protocolo={protocol_name}")
        return operation, filename, protocol_name
        


    def _execute_operation(self, operation, path):
        if operation == "UPLOAD":
                self.protocol.recv_file(path)
        elif operation == "DOWNLOAD":
            if not os.path.exists(path):
                logging.error(f"Archivo no encontrado: {path}")
                packet_error = Packet.build(DATA, 0, b"ERROR|FILE_NOT_FOUND")
                self.protocol._send(packet_error)
                return
            self.protocol.send_file(path)

    def _init_protocol(self, protocol_name):
        if protocol_name.lower() == 'gbn':
            logging.debug(f"Inicializando protocolo Go-Back-N para {self.peer_addr}")
            self.protocol = gbn.GoBackNProtocol(self.own_socket, self.peer_addr)
        elif protocol_name.lower() == 'snw':
            logging.debug(f"Inicializando protocolo Stop-and-Wait para {self.peer_addr}")
            self.protocol = snw.StopNWaitProtocol(self.own_socket, self.peer_addr)
        else:
            logging.error(f"Protocolo desconocido: {protocol_name}")
            packet_error = Packet.build(DATA, 0, b"ERROR|UNKNOWN_PROTOCOL")
            self.own_socket.sendto(packet_error, self.peer_addr)
            return False
        return True

    def stop(self):
        if self.protocol:
            self.protocol.request_stop()