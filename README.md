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

## /api/stream/\<id\>

Use POST to stream recorded sound packets to our server for further analysis.

## /visualize/\<sessionID\>

Data visualization for *sessionID* recording session.
