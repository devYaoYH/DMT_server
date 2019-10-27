import socket
import pickle
import json
import numpy as np
import scipy.io.wavfile
scipy_wav = scipy.io.wavfile

BUF_SIZE = 4096
PKT_HEADER = 4

WAV_DIR = '/home/yaoyiheng/session/'
SOUNDS = dict()
SESSIONS = dict()
SOUNDS_IDX = 0

# PACKET TYPES
PKT_INIT = 0
PKT_STREAM = 1
PKT_VIEW = 2
PKT_DOWNLOAD = 3

def digest_packet(json_dump):
    pkt = json.loads(json_dump)
    if (pkt['type'] == PKT_INIT):
        sessionID = pkt['sessionID']
        sample_rate = int(pkt['rate'])
        if (sessionID in SESSIONS):
            for s_id in SESSIONS[sessionID]:
                del SOUNDS[s_id]
            del SESSIONS[sessionID]
        SESSIONS[sessionID] = [SOUNDS_IDX]
        SOUNDS[SOUNDS_IDX] = {'data': [], 'rate': sample_rate}
        url = f'/api/stream/{SOUNDS_IDX}'
        SOUNDS_IDX += 1
        return json.dumps({'success': True, 'url': url, 'session': sessionID})
    elif (pkt['type'] == PKT_STREAM):
        soundID = int(pkt['soundID'])
        pkt_idx = int(pkt['index'])
        pkt_data = json.loads(pkt['data'])
        if (soundID not in SOUNDS):
            return json.dumps({'success': False, 'log': 'session/sound NOT EXIT'})
        else:
            SOUNDS[soundID]['data'].append((pkt_idx, pkt_data))
            return json.dumps({'success': True, 'log': f'pkt {pkt_idx} loaded into db'})
    elif (pkt['type'] == PKT_VIEW):
        sessionID = pkt['sessionID']
        if (sessionID not in SESSIONS):
            return json.dumps({'success': False, 'log': f'{sessionID} Does not EXIST'})
        else:
            return json.dumps({'success': True, 'log': f'{list(SESSIONS[sessionID])}'})
    elif (pkt['type'] == PKT_DOWNLOAD):
        sessionID = pkt['sessionID']
        soundID = int(pkt['soundID'])
        if (soundID in SOUNDS and sessionID in SESSIONS and soundID in SESSIONS[sessionID]):
            fname = f"{WAV_DIR}{sessionID}_{soundID}.wav"
            if (not os.path.isfile(fname)):
                scipy_wav.write(fname, SOUNDS[soundID]['rate'], np.asarray(sorted(SOUNDS[soundID]['data'], key=lambda x: x[0])[:, 1]))
            return json.dumps({'success': True, 'url': fname})
        else:
            return json.dumps({'success': False, 'log': f'File {soundID} does not exist for session {sessionID}'})

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
            
            # Do stuff to packet
            send_pkt = pickle.dumps(digest_packet(pickle.loads(recv_pkt)))
            
            # Respond
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
