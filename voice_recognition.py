import speech_recognition as sr
import logging
import asyncio
import numpy as np
import simpleaudio as sa
from gtts import gTTS
import os
import subprocess

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a timeout value for the listen() method
LISTEN_TIMEOUT = 60  # Adjust this value based on your requirements

async def recognize_voice():
    logging.info("recognize_voice running.")
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # Find the microphone by name containing the word "index"
    microphone_list = sr.Microphone.list_microphone_names()

    # Format the microphone list with one microphone per line
    formatted_microphone_list = "\n".join(microphone_list)
    logging.info(f"Available Microphones:\n{formatted_microphone_list}")

    async def play_tone_sequence(sequence):
        for tone in sequence:
            frequency, duration, volume = tone
            await play_tone(frequency, duration, volume)

    async def play_tone(frequency, duration, volume):
        # Generate samples for the specified frequency and duration
        sample_rate = 44100  # Standard audio sample rate (can be adjusted if needed)
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio = np.sin(frequency * 2 * np.pi * t)

        # Adjust the volume of the audio
        audio *= volume

        # Convert the samples to the appropriate data type
        audio = (audio * 32767).astype(np.int16)

        # Play the audio
        play_obj = sa.play_buffer(audio, 1, 2, sample_rate)
        play_obj.wait_done()

    with microphone as source:
        while True:
            try:
                temp_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp.mp3")
                # Remove existing temporary audio file if it exists
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                # Play the tone sequence for the start sound
                sequence = [(440, 0.2, 0.2), (660, 0.2, 0.3), (880, 0.2, 0.2)]  # Adjust tones, durations, and volumes as desired
                asyncio.create_task(play_tone_sequence(sequence))

                logging.debug("Listening to microphone...")
                audio_data = recognizer.listen(source, timeout=LISTEN_TIMEOUT)
                logging.debug("Audio data captured.")

                # Use the speech recognition library to transcribe the voice input
                logging.debug("Recognizing voice input...")
                text = recognizer.recognize_google(audio_data).lower()
                logging.info(f"Recognized voice input: {text}")

                message = text.strip()
                with open('flag.info', 'w') as file:
                    file.write(message)
                # Convert the phrase "Understood" into speech
                tts = gTTS(message)
                # Save the speech as an audio file in the script's 
                tts.save(temp_filename)
                # Play the audio file using Windows Media Player
                subprocess.Popen(["C:\\Program Files (x86)\\Windows Media Player\\wmplayer.exe", temp_filename])

            except sr.WaitTimeoutError:
                # Handle timeout event and continue the loop to relaunch the listen process
                continue
            except sr.UnknownValueError:
                # Handle cases where the speech recognition couldn't understand the voice input
                message = "Could not understand the voice input"
                with open('flag.info', 'w') as file:
                    file.write(message)
            except sr.RequestError:
                # Handle errors from the speech recognition service
                message = "Speech recognition service error"
                with open('flag.info', 'w') as file:
                    file.write(message)

            await asyncio.sleep(0.1)  # Add a small delay to allow other tasks to run

async def main():
    await recognize_voice()

if __name__ == "__main__":
    asyncio.run(main())
