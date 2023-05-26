# Seraphim
A Basice voice recognition system to send data over a websocket, originally made for use in VR applications.

## How it works
- Run the Websocket script
- Connect to it
- Send start to begin recording
- Speak and validate the response was said back correctly
- Send stop to receive the understood phrase over the websocket

## External Requirements
- speech_recognition
- simpleaudio
- gtts
- numpy

```
pip install SpeechRecognition
pip install simpleaudio
pip install gtts
pip install numpy
```
## Internal Requirements
- logging
- asyncio
- os
- subprocess
