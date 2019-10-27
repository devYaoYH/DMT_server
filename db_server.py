import socket
import pickle
import json

BUF_SIZE = 12
PKT_HEADER = 4

def run_server(ADDR):
    host, port = ADDR

    server_socket = socket.socket()
    server_socket.bind((host, port))
    
    server_socket.listen()

    while True:
        conn, addr = server_socket.accept()
        with conn:
            print("connected by:", addr)
            recv_pkt = bytearray()
            recv_size = bytearray(conn.recv(PKT_HEADER))
            recv_size = (int(recv_size[0]) << 24) + (int(recv_size[1]) << 16) + (int(recv_size[2]) << 8) + int(recv_size[3])
            while len(recv_pkt) < recv_size:
                data = conn.recv(min(BUF_SIZE, recv_size - len(recv_pkt)))
                recv_pkt.extend(data)
            print(f"Server received {recv_pkt}")
            send_pkt = recv_pkt
            send_pkt_len = len(send_pkt)
            print(f"Server sending {send_pkt_len} bytes")
            pkt_len = bytearray()
            pkt_len.append((send_pkt_len >> 24)&255)
            pkt_len.append((send_pkt_len >> 16)&255)
            pkt_len.append((send_pkt_len >> 8)&255)
            pkt_len.append(send_pkt_len&255)
            print(f"Server sending {pkt_len} bytes")
            conn.send(pkt_len)
            conn.sendall(send_pkt)

if __name__ == '__main__':
    HOST = 'localhost'
    PORT = 31234
    ADDR = (HOST, PORT)

    run_server(ADDR)
