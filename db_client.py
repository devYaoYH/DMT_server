import socket
import pickle
import json

BUF_SIZE = 16
PKT_HEADER = 2

def run_client(ADDR):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(ADDR)
        s.sendall(pickle.dumps(json.dumps({'data': "stuff", 'label': [0, 2, 23, 4, 2, 1]})))
        pkt_size = bytearray(s.recv(PKT_HEADER))
        pkt_size = (int(pkt_size[0]) << 8) + int(pkt_size[1])
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

if __name__ == '__main__':
    HOST = 'localhost'
    PORT = 31234
    ADDR = (HOST, PORT)

    run_client(ADDR)
