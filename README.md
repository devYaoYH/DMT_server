# Server API endpoints

## /api/init

POST to /api/init with correctly formatted handshake packet to initialize recording of audio data.

```
{
    'rate': <Int> Polling rate (Bits/sec),
    'sessionID': <String> Recording session ID (Unique Identifier),
    'location': <String> GPS location
}
```

We will respond with json:
```
{
    'success': True/False,
    'url': some url to post audio data to
}
```

## /api/stream/\<id\>

Use POST to stream recorded sound packets to our server for further analysis.

## /view/\<sessionID\>

Data visualization for *sessionID* recording session.

## /api/analyze/\<sessionID\>/\<fileID\>

Get some analysis data from Tim's utils (return json):
```
{
    'noise': <float> noise level,
    'ifft': [<float>] array of values with ifft smoothened audio (last 50ms)
}
```
