import asyncio
import websockets
import logging
import traceback
import subprocess
import os
import colorama
import tkinter as tk
from tkinter import messagebox

# Configure logging
colorama.init()  # Initialize colorama for cross-platform colored output
import logging  # Import logging module here

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Process for running voice recognition
voice_process = None

async def handle_start_stop_command(command):
    global voice_process

    if command == "start" and voice_process is None:
        voice_process = subprocess.Popen(["python", "voice_recognition.py"], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        logging.info(colorama.Fore.BLUE + "Voice recognition started." + colorama.Style.RESET_ALL)
        return "Voice recognition started."

    elif command == "stop" and voice_process is not None:
        voice_process.terminate()
        voice_process = None
        logging.info(colorama.Fore.BLUE + "Voice recognition stopped." + colorama.Style.RESET_ALL)
        return "Voice recognition stopped."

    else:
        return "Invalid command."

async def server_handler(websocket, path):
    try:
        while True:
            if os.path.isfile('flag.info'):
                with open('flag.info', 'r') as file:
                    current_message = file.read()

                if current_message != "":
                    print(colorama.Fore.WHITE + current_message + colorama.Style.RESET_ALL)  # Print incoming messages in white
                    await websocket.send(current_message)  # Send the incoming message to the client
                    os.remove('flag.info')  # Remove the file after reading
                else:
                    await asyncio.sleep(0.1)

            try:
                command = await websocket.recv()

                if command in ['start', 'stop']:
                    response = await handle_start_stop_command(command)
                    if command == 'start':
                        print(colorama.Fore.YELLOW + response + colorama.Style.RESET_ALL)  # Print outgoing messages in yellow

            except websockets.exceptions.ConnectionClosedError:
                traceback.print_exc()  # Print the traceback of the exception
                break  # Exit the loop if the connection is closed

    except websockets.exceptions.ConnectionClosed:
        pass  # Connection was closed by the client

async def start_server(port):
    while True:
        try:
            async with websockets.serve(server_handler, 'localhost', port):
                logging.info(colorama.Fore.BLUE + f"Server started on port {port}" + colorama.Style.RESET_ALL)
                await asyncio.Future()  # Keep the server running indefinitely
                break  # Exit the loop if the server is closed successfully
        except OSError:
            logging.warning(colorama.Fore.YELLOW + f"Port {port} is not available. Trying the next port." + colorama.Style.RESET_ALL)
            port += 1

def configure_port():
    if os.path.isfile('port.info'):
        with open('port.info', 'r') as file:
            return int(file.read())

    def save_port():
        new_port = port_entry.get()
        if new_port.isdigit():
            with open('port.info', 'w') as file:
                file.write(new_port)
            root.destroy()
        else:
            messagebox.showerror("Invalid Port", "Port must be a positive integer.")

    root = tk.Tk()
    root.title("Configure Port")
    root.geometry("300x100")

    port_label = tk.Label(root, text="Enter Port:")
    port_label.pack()

    port_entry = tk.Entry(root)
    port_entry.pack()

    save_button = tk.Button(root, text="Save", command=save_port)
    save_button.pack()

    root.mainloop()

    return configure_port()

def main():
    port = configure_port()
    asyncio.get_event_loop().create_task(start_server(port))
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
