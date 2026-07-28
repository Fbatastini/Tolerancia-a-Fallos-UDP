import struct

HEADER_FORMAT = '!BI'  # Type (1 byte) + Sequence Number (4 bytes)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
PAYLOAD_SIZE = 1024 - HEADER_SIZE

DATA = 0
ACK = 1
SYN = 2
FIN = 3

class Packet:
    @staticmethod
    def build(type, seq_num, playload=b''):
        header = struct.pack('!BI', type, seq_num)
        return header + playload
    
    @staticmethod
    def parse(packet):
        header = packet[:HEADER_SIZE]
        playload = packet[HEADER_SIZE:]
        packet_type, seq_num = struct.unpack(HEADER_FORMAT, header)
        return packet_type, seq_num, playload