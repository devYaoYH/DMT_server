import socket
import pickle
import os
import sys
import json
import util
import numpy as np
import scipy.io.wavfile
scipy_wav = scipy.io.wavfile
util = util.util

BUF_SIZE = 4096
PKT_HEADER = 4

SAMPLE_WINDOW = 50

WAV_DIR = '/home/yaoyiheng/session/'
SOUNDS = dict()
SESSIONS = dict()
SOUNDS_IDX = 0

# PACKET TYPES
PKT_INIT = 0
PKT_STREAM = 1
PKT_VIEW = 2
PKT_DOWNLOAD = 3
PKT_QUERY = 4

def digest_packet(json_dump):
    global SOUNDS
    global SESSIONS
    global SOUNDS_IDX
    pkt = json.loads(json_dump)
    if (pkt['type'] == PKT_INIT):
        sessionID = pkt['sessionID']
        sample_rate = int(pkt['rate'])
        if (sessionID in SESSIONS):
            SESSIONS[sessionID].append(SOUNDS_IDX)
        else:
            SESSIONS[sessionID] = [SOUNDS_IDX]
        SOUNDS[SOUNDS_IDX] = {'data': [], 'rate': sample_rate}
        url = f'/api/stream/{SOUNDS_IDX}'
        SOUNDS_IDX += 1
        return json.dumps({'success': True, 'url': url, 'session': sessionID})
    elif (pkt['type'] == PKT_STREAM):
        soundID = int(pkt['soundID'])
        pkt_idx = int(pkt['index'])
        pkt_data = pkt['data']
        if (soundID not in SOUNDS):
            return json.dumps({'success': False, 'log': 'session/sound NOT EXIT'})
        else:
            SOUNDS[soundID]['data'].append((pkt_idx, pkt_data))
            return json.dumps({'success': True, 'log': f'pkt {pkt_idx} loaded into db'})
    elif (pkt['type'] == PKT_VIEW):
        if ('sessionID' not in pkt):
            return json.dumps({'success': True, 'log': f'{json.dumps({k: v for k, v in SESSIONS.items()})}'})
        else:
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
            print(f"Attempted download of file: {fname}", file=sys.stderr)
            if (not os.path.isfile(fname)):
                if (len(SOUNDS[soundID]['data']) == 0):
                    return json.dumps({'success': False, 'log': f'{soundID} has no data'})
                raw_arr = sorted(SOUNDS[soundID]['data'], key=lambda x: x[0])
                data_arr = []
                for t in raw_arr:
                    data_arr.extend(t[1])
                print(data_arr[:10], file=sys.stderr)
                scipy_wav.write(fname, SOUNDS[soundID]['rate'], np.asarray(data_arr))
            sample_window = -SOUNDS[soundID]['rate']//1000*SAMPLE_WINDOW
            print(f'Keeping {sample_window} in memory')
            del SOUNDS[soundID]['data'][:sample_window]
            return json.dumps({'success': True, 'url': f'{sessionID}_{soundID}.wav'})
        else:
            return json.dumps({'success': False, 'log': f'File {soundID} does not exist for session {sessionID}'})
    elif (pkt['type'] == PKT_QUERY):
        sessionID = pkt['sessionID']
        soundID = int(pkt['soundID'])
        if (soundID in SOUNDS and sessionID in SESSIONS and soundID in SESSIONS[sessionID]):
            sample_window = -SOUNDS[soundID]['rate']//1000*SAMPLE_WINDOW
            raw_data = sorted(SOUNDS[soundID]['data'][max(0, len(SOUNDS[soundID]['data'])+sample_window):])
            sample_data = []
            for t in raw_data:
                sample_data.extend(t[1])
            ret_pkt = dict()
            ret_pkt['noise'] = util.smoothnessAccessAverage(SOUNDS[soundID]['rate'], sample_data, 3)
            ret_pkt['ifft'] = util.smoothIFFT(SOUNDS[soundID]['rate'], sample_data, 3)
            ret_pkt['success'] = True
            return json.dumps(ret_pkt)
        else:
            ret_pkt['success'] = False
            return json.dumps(ret_pkt)
        

def run_server(ADDR, debug=False):
    host, port = ADDR

    server_socket = socket.socket()
    server_socket.bind((host, port))
    
    server_socket.listen()

    while True:
        conn, addr = server_socket.accept()
        with conn:
            if (debug):
                print("connected by:", addr)
            recv_pkt = bytearray()
            recv_size = bytearray(conn.recv(PKT_HEADER))
            recv_size = (int(recv_size[0]) << 24) + (int(recv_size[1]) << 16) + (int(recv_size[2]) << 8) + int(recv_size[3])
            while len(recv_pkt) < recv_size:
                data = conn.recv(min(BUF_SIZE, recv_size - len(recv_pkt)))
                recv_pkt.extend(data)
            if (debug):
                print(f"Server received {recv_pkt}")
            
            # Do stuff to packet
            send_pkt = pickle.dumps(digest_packet(pickle.loads(recv_pkt)))
            
            # Respond
            send_pkt_len = len(send_pkt)
            if (debug):
                print(f"Server sending {send_pkt_len} bytes")
            pkt_len = bytearray()
            pkt_len.append((send_pkt_len >> 24)&255)
            pkt_len.append((send_pkt_len >> 16)&255)
            pkt_len.append((send_pkt_len >> 8)&255)
            pkt_len.append(send_pkt_len&255)
            if (debug):
                print(f"Server sending {pkt_len} bytes")
            conn.send(pkt_len)
            conn.sendall(send_pkt)

if __name__ == '__main__':
    HOST = 'localhost'
    PORT = 31234
    ADDR = (HOST, PORT)

    run_server(ADDR)
