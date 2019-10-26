from flask import Flask
from flask import request
import json
app = Flask(__name__)

SOUNDS_IDX = 0
SOUNDS = dict()

@app.route('/')
def hello_world():
    return "Hello Sounds!"

@app.route('/api/init', methods = ['POST'])
def init_sound():
    global SOUNDS_IDX
    global SOUNDS
    if request.method == 'POST':
        data = request.json
        url = f'/api/stream/{SOUNDS_IDX}'
        SOUNDS[SOUNDS_IDX] = {'data': '', 'index': 0}
        SOUNDS_IDX += 1
        return url
    return "None"

@app.route('/api/stream/<sound_id>', methods = ['POST'])
def stream(sound_id):
    global SOUNDS
    if request.method == 'POST':
        data = request.json
        if ('data' in data and 'index' in data):
            # Build up our file
            if (sound_id not in SOUNDS):
                return "Song NOT Initialized"
            else:
                SOUNDS[sound_id]['data'] += data['data']
                SOUNDS[sound_id]['index'] += 1
            return f"{sound_id}: {SOUNDS[sound_id]['data']}"
        else:
            return "Malformed Packet"
    return "None"

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
    app.run()
