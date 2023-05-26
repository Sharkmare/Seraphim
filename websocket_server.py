import asyncio
import websockets
import logging
import aiofiles
import traceback
import subprocess
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Process for running voice recognition
voice_process = None

async def handle_start_stop_command(command):
    global voice_process

    if command == "start" and voice_process is None:
        voice_process = subprocess.Popen(["python", "voice_recognition.py"], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        logging.info("Voice recognition started.")
        return "Voice recognition started."

    elif command == "stop" and voice_process is not None:
        voice_process.terminate()
        voice_process = None
        logging.info("Voice recognition stopped.")
        return "Voice recognition stopped."

    else:
        return "Invalid command."

async def server_handler(websocket, path):
    try:
        if not os.path.isfile('flag.info'):
            with open('flag.info', 'w') as file:
                file.write('')

        while True:
            async with aiofiles.open('flag.info', 'r') as file:
                current_message = await file.read()

            if current_message != "":
                await websocket.send(current_message)
                with open('flag.info', 'w') as file:
                    file.write('')
            else:
                 await websocket.send("")

            try:
                command = await asyncio.gather(websocket.recv(), aiofiles.open('flag.info', 'r'), return_exceptions=True)

                if isinstance(command[0], str) and command[0] in ['start', 'stop']:
                    response = await handle_start_stop_command(command[0])
                    if command[0] == 'start':
                        await websocket.send(response)
                elif isinstance(command[1], aiofiles.threadpool.binary.AsyncBufferedIOBase):
                    current_message = await command[1].read()
                    await websocket.send(current_message)
                    with open('flag.info', 'w') as file:
                        file.write('')

            except websockets.exceptions.ConnectionClosedError:
                traceback.print_exc()  # Print the traceback of the exception
                break  # Exit the loop if the connection is closed

    except websockets.exceptions.ConnectionClosed:
        pass  # Connection was closed by the client

async def start_server():
    server = await websockets.serve(server_handler, 'localhost', 8765)
    await server.wait_closed()

async def main():
    await start_server()

if __name__ == "__main__":
    asyncio.run(main())
