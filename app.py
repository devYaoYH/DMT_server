from flask import Flask
from flask import request
from flask import send_from_directory
import os
import json
import numpy as np
import scipy.io.wavfile
import db_client
app = Flask(__name__)

scipy_wav = scipy.io.wavfile

ADDR = ('localhost', 31234)
PKT_INIT = 0
PKT_STREAM = 1
PKT_VIEW - 2
PKT_DOWNLOAD = 3

@app.route('/')
def hello_world():
    return "Hello Sounds!"

@app.route('/api/init', methods = ['POST'])
def init_sound():
    if request.method == 'POST':
        data = request.json
        if ('sessionID' in data):
            sessionID = data['sessionID']
        data['type'] = PKT_INIT
        return db_client.send_pkt(ADDR, json.dumps(data))
    return json.dumps({'success': False})

@app.route('/view/<sessionID>')
def view_session(sessionID):
    req_view = dict()
    req_view['sessionID'] = sessionID
    req_view['type'] = PKT_VIEW
    return db_client.send_pkt(ADDR, json.dumps(req_view))

@app.route('/view/<sessionID>/<fileID>')
def view_wav(sessionID, fileID):
    req_dl = dict()
    req_dl['sessionID'] = sessionID
    req_dl['soundID'] = fileID
    req_dl['type'] = PKT_DOWNLOAD
    return db_client.send_pkt(ADDR, json.dumps(req_dl))

@app.route('/api/stream/<sound_id>', methods = ['POST'])
def stream(sound_id):
    if request.method == 'POST':
        data = request.json
        data['data'] = [float(f) for f in json.loads(data['data'])]
        req_stream = data
        req_stream['type'] = PKT_STREAM
        return db_client.send_pkt(ADDR, json.dumps(req_stream))
    return json.dumps({'success': False, 'log': "Not a POST"})

@app.route('/countme/<input_str>')
def count_me(input_str):
    counter = dict()
    for c in input_str:
        try:
            counter[c] += 1
        except KeyError:
            counter[c] = 1
    response = [f"STRING: {input_str}"]
    for key, val in counter.items():
        response.append(f"{key}:{val}")
    return '<br>'.join(response)

if __name__ == '__main__':
    app.run(debug=True)
