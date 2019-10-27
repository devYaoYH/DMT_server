from flask import Flask
from flask import request
from flask import send_from_directory
import os
import json
import numpy as np
import scipy.io.wavfile
app = Flask(__name__)
UPLOAD_FOLDER = '/home/yaoyiheng/session/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

scipy_wav = scipy.io.wavfile

SOUNDS_IDX = 0
SOUNDS = dict()
SESSIONS = dict()

@app.route('/')
def hello_world():
    return "Hello Sounds!"

@app.route('/api/init', methods = ['POST'])
def init_sound():
    global SOUNDS_IDX
    global SOUNDS
    global SESSIONS
    if request.method == 'POST':
        data = request.json
        if ('sessionID' in data):
            sessionID = data['sessionID']
            try:
                SESSIONS[sessionID].append(SOUNDS_IDX)
            except:
                SESSIONS[sessionID] = [SOUNDS_IDX]
        url = f'/api/stream/{SOUNDS_IDX}'
        SOUNDS[SOUNDS_IDX] = {'data': [], 'index': 0, 'rate': int(data['rate']), 'log': []}
        SOUNDS_IDX += 1
        return json.dumps({'success': True, 'url': url, 'session': sessionID})
    return json.dumps({'success': False})

@app.route('/view/<sessionID>')
def view_session(sessionID):
    global SESSIONS
    global SOUNDS
    if (sessionID not in SESSIONS):
        return f"ERROR: {sessionID} not init"
    for s_id in SESSIONS[sessionID]:
        sound_data = SOUNDS[s_id]['data']
        # Check if file exists before writing
        sound_file = f"{app.config['UPLOAD_FOLDER']}{sessionID}_{s_id}.wav"
        if (not os.path.isfile(sound_file)):
            # Save as wav file
            scipy_wav.write(f"{app.config['UPLOAD_FOLDER']}{sessionID}_{s_id}.wav", SOUNDS[s_id]['rate'], np.asarray(sound_data))
            del SOUNDS[s_id]['data'][:]
    return json.dumps({'success': True, 'log': SESSIONS[sessionID]})
    #return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=f'{sessionID}_{s_id}.wav', as_attachment=True)

@app.route('/view/<sessionID>/<fileID>')
def view_wav(sessionID, fileID):
    link = f'35.193.212.185/view/raw/{sessionID}/{fileID}'
    try:
        log = SOUNDS[fileID]['log']
        return json.dumps({'success': True, 'link': link, 'log': log})
    except:
        return json.dumps({'success': False})

@app.route('/view/raw/<sessionID>/<fileID>')
def download_wav(sessionID, fileID):
    sound_file = f"{app.config['UPLOAD_FOLDER']}{sessionID}_{fileID}.wav"
    if (os.path.isfile(sound_file)):
        return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=f'{sessionID}_{fileID}.wav', as_attachment=True)
    return "NO File Exists"

@app.route('/api/stream/<sound_id>', methods = ['POST'])
def stream(sound_id):
    global SOUNDS
    sound_id = int(sound_id)
    if request.method == 'POST':
        data = request.json
        if ('data' in data and 'index' in data):
            # Build up our file
            if (sound_id not in SOUNDS):
                return json.dumps({'success': False, 'log': "Song NOT Initialized", 'keys': list(SOUNDS.keys())})
            else:
                try:
                    SOUNDS[sound_id]['data'].extend([float(f) for f in json.loads(data['data'])])
                    SOUNDS[sound_id]['index'] += 1
                    SOUNDS[sound_id]['log'].append(data['index'])
                except Exception as e:
                    return json.dumps({'success': False, 'log': f"Data formatting error {str(e)}"})
            return json.dumps({'success': True, 'data': f"{sound_id}: {SOUNDS[sound_id]['data']}"})
        else:
            return json.dumps({'success': False, 'log': "Malformed Packet"})
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
