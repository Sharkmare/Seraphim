import asyncio
import websockets
import speech_recognition as sr
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a timeout value for the listen() method
LISTEN_TIMEOUT = 5  # Adjust this value based on your requirements

async def handle_command(command):
    # Implement your command handling logic here based on the input command
    if "trigger event" in command:
        response = "Triggering event"
    elif "do something" in command:
        response = "Doing something"
    else:
        response = "Unknown command"

    return response

async def recognize_voice(websocket, path):
    logging.info("recognize_voice running.")
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # Find the microphone by name containing the word "index"
    microphone_list = sr.Microphone.list_microphone_names()

    # Format the microphone list with one microphone per line
    formatted_microphone_list = "\n".join(microphone_list)
    logging.info(f"Available Microphones:\n{formatted_microphone_list}")

    activation_phrase = "overwatch"
    is_activated = False

    with microphone as source:
        while True:
            try:
                # Listen to the microphone for voice input with a timeout
                logging.debug("Listening to microphone...")
                audio_data = recognizer.listen(source, timeout=LISTEN_TIMEOUT)
                logging.debug("Audio data captured.")

                # Use the speech recognition library to transcribe the voice input
                logging.debug("Recognizing voice input...")
                text = recognizer.recognize_google(audio_data).lower()
                logging.info(f"Recognized voice input: {text}")
    
                if not is_activated:
                    if activation_phrase == text:
                        is_activated = True
                        logging.info("Activation phrase recognized. System activated.")
                        response = "Activated. Waiting for command..."
                    else:
                        response = "Not activated. Listening for activation phrase..."
                else:
                    response = await handle_command(text)
                    is_activated = False  # Deactivate after analyzing the command
                    logging.info("Command processed. System deactivated. Listening for activation phrase...")

                if websocket:
                    await websocket.send(response)

            except sr.WaitTimeoutError:
                # Handle timeout event and continue the loop to relaunch the listen process
                logging.debug("Timeout occurred while waiting for speech")
                continue
            except sr.UnknownValueError:
                # Handle cases where the speech recognition couldn't understand the voice input
                response = "Could not understand the voice input"
                if websocket:
                    await websocket.send(response)
            except sr.RequestError:
                # Handle errors from the speech recognition service
                response = "Speech recognition service error"
                if websocket:
                    await websocket.send(response)

async def start_server():
    server = await websockets.serve(recognize_voice, 'localhost', 8765)
    await server.wait_closed()

# Run the server and the recognize_voice coroutine concurrently
async def run_server():
    server_task = asyncio.create_task(start_server())
    voice_task = asyncio.create_task(recognize_voice(None, None))
    await asyncio.gather(server_task, voice_task)

asyncio.run(run_server())
