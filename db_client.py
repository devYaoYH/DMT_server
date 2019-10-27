import sys
import socket
import pickle
import json

BUF_SIZE = 4096
PKT_HEADER = 4

def run_client(ADDR):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(ADDR)
        send_bytes = pickle.dumps(json.dumps({'args': "" if len(sys.argv) < 2 else sys.argv[1], 'label': [0, 2, 23, 4, 2, 1]}))
        send_len = bytearray()
        send_len.append((len(send_bytes)>> 24)&255)
        send_len.append((len(send_bytes)>> 16)&255)
        send_len.append((len(send_bytes)>> 8)&255)
        send_len.append(len(send_bytes)&255)
        s.send(send_len)
        s.sendall(send_bytes)
        pkt_size = bytearray(s.recv(PKT_HEADER))
        pkt_size = (int(pkt_size[0]) << 24) + (int(pkt_size[1]) << 16) + (int(pkt_size[2]) << 8) + int(pkt_size[3])
        print(f"Client receiving {pkt_size} bytes")
        ret_pkt = bytearray()
        data = s.recv(min(BUF_SIZE, pkt_size - len(ret_pkt)))
        print("client:", data)
        while len(ret_pkt) < pkt_size:
            ret_pkt.extend(data)
            print(f"client waiting for: {min(BUF_SIZE, pkt_size - len(ret_pkt))} bytes")
            data = s.recv(min(BUF_SIZE, pkt_size - len(ret_pkt)))
            print("client:", data)
        print("Echo:", pickle.loads(ret_pkt))

# Our pkt is a json.dumps object
def send_pkt(ADDR, pkt):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(ADDR)
        send_bytes = pickle.dumps(pkt)
        send_len = bytearray()
        send_len.append((len(send_bytes)>> 24)&255)
        send_len.append((len(send_bytes)>> 16)&255)
        send_len.append((len(send_bytes)>> 8)&255)
        send_len.append(len(send_bytes)&255)
        s.send(send_len)
        s.sendall(send_bytes)
        pkt_size = bytearray(s.recv(PKT_HEADER))
        pkt_size = (int(pkt_size[0]) << 24) + (int(pkt_size[1]) << 16) + (int(pkt_size[2]) << 8) + int(pkt_size[3])
        print(f"Client receiving {pkt_size} bytes")
        ret_pkt = bytearray()
        data = s.recv(min(BUF_SIZE, pkt_size - len(ret_pkt)))
        while len(ret_pkt) < pkt_size:
            ret_pkt.extend(data)
            data = s.recv(min(BUF_SIZE, pkt_size - len(ret_pkt)))
        ret_pkt = pickle.loads(ret_pkt)
        print("Received pkt:", ret_pkt)
        return ret_pkt

if __name__ == '__main__':
    HOST = 'localhost'
    PORT = 31234
    ADDR = (HOST, PORT)

    run_client(ADDR)
