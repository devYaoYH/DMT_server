from flask import Flask
from flask import request
from flask import send_from_directory
from flask import render_template
import os
import sys
import json
import db_client
app = Flask(__name__)

ADDR = ('localhost', 31234)
PKT_INIT = 0
PKT_STREAM = 1
PKT_VIEW = 2
PKT_DOWNLOAD = 3
PKT_QUERY = 4
WAV_DIR = '/home/yaoyiheng/session/'

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/demo')
def visual_js():
    return render_template('demo.html')

@app.route('/api/init', methods = ['POST'])
def init_sound():
    if request.method == 'POST':
        data = request.json
        if ('sessionID' in data):
            sessionID = data['sessionID']
        data['type'] = PKT_INIT
        return db_client.send_pkt(ADDR, json.dumps(data))
    return json.dumps({'success': False})

@app.route('/view')
def view_all():
    req_view = dict()
    req_view['type'] = PKT_VIEW
    return db_client.send_pkt(ADDR, json.dumps(req_view))

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
    print("Clinet Requested for FILE\n", req_dl, file=sys.stderr)
    ret_pkt = json.loads(db_client.send_pkt(ADDR, json.dumps(req_dl)))
    if (ret_pkt['success']):
        return send_from_directory(directory=WAV_DIR, filename=ret_pkt['url'], as_attachment=True)
    else:
        return json.dumps(ret_pkt)

@app.route('/api/analyze/<sessionID>/<fileID>')
def get_analysis(sessionID, fileID):
    req_analysis = dict()
    req_analysis['sessionID'] = sessionID
    req_analysis['soundID'] = fileID
    req_analysis['type'] = PKT_QUERY
    ret_pkt = json.loads(db_client.send_pkt(ADDR, json.dumps(req_analysis)))
    return json.dumps(ret_pkt)

@app.route('/api/stream/<sound_id>', methods = ['POST'])
def stream(sound_id):
    if request.method == 'POST':
        data = request.json
        data['soundID'] = sound_id
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
