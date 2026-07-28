import socket
import lib.common.protocol as Protocol
import lib.common.go_back_n as gbn
import lib.common.stop_n_wait as snw
import logging
import lib.common.logs as Logs
import time

SEQ_NUMBER_ERROR = 0

def init_connection(protocol_name, server_address, action, filename, local_filepath=None):
    t = time.time()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if protocol_name == 'gbn':
        logging.debug(f"Inicializando protocolo Go-Back-N para el cliente")
        protocol = gbn.GoBackNProtocol(client_socket, server_address)
    elif protocol_name == 'snw':
        logging.debug(f"Inicializando protocolo Stop-and-Wait para el cliente")
        protocol = snw.StopNWaitProtocol(client_socket, server_address)

    metadata = f"{action}|{filename}|{protocol_name}".encode()
    
    logging.debug(f"Enviando SYN con metadata: {metadata.decode()}")

    protocol.send_syn(metadata)
    
    try:
        if action == 'UPLOAD':
            protocol.send_file(local_filepath)
        elif action == 'DOWNLOAD':
            try:
                pkt_data, _ = protocol._recv()
                pkt_type, _, payload = pkt_data

                if payload.startswith(b"ERROR|"):
                    logging.error(payload.decode())
                    return
            except socket.timeout:
                pass

            protocol.recv_file(local_filepath)
    except Exception as e:
        logging.error(f"Error durante {action.lower()}: {e}")
    except KeyboardInterrupt:
        logging.info("Interrupción por teclado, cerrando conexión")
        if 'protocol' in locals():
            protocol.send_fin(SEQ_NUMBER_ERROR)
    finally:        
        if 'protocol' in locals():
            protocol.stop()
        client_socket.close()
        tf = time.time()
        print(f"Tiempo total de transferencia: {tf - t} segundos")
