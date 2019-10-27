import socket
import pickle

def run_server():
    host = socket.gethostname()
    port = 31234

    server_socket = socket.socket()
    server_socket.bind((host, port))
    
    server_socket.listen()
    

if __name__ == '__main__':
    run_server()
