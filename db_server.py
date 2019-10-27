import socket
import pickle
import json

def run_server(ADDR):
    host, port = ADDR

    server_socket = socket.socket()
    server_socket.bind((host, port))
    
    server_socket.listen()

    while True:
        conn, addr = server_socket.accept()
        with conn:
            print("connected by:", addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                send_pkt = pickle.dumps(data)
                send_pkt_len = len(send_pkt)
                print(f"Server sending {send_pkt_len} bytes")
                pkt_len = bytearray()
                pkt_len.append((send_pkt_len >> 8)&255)
                pkt_len.append(send_pkt_len&255)
                print(f"Sending {pkt_len} bytes")
                conn.send(pkt_len)
                conn.sendall(data)

if __name__ == '__main__':
    HOST = 'localhost'
    PORT = 31234
    ADDR = (HOST, PORT)

    run_server(ADDR)
