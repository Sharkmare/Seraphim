import speech_recognition as sr
import logging
import asyncio
import winsound

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

    activation_phrase = "overwatch"
    
    with microphone as source:
        while True:
            try:
                # Listen to the microphone for voice input with a timeout
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                logging.debug("Listening to microphone...")
                audio_data = recognizer.listen(source, timeout=LISTEN_TIMEOUT)
                logging.debug("Audio data captured.")

                # Use the speech recognition library to transcribe the voice input
                logging.debug("Recognizing voice input...")
                text = recognizer.recognize_google(audio_data).lower()
                logging.info(f"Recognized voice input: {text}")

                if activation_phrase in text or True:
                    message = text.replace(activation_phrase, "").strip()
                    with open('flag.info', 'w') as file:
                        file.write(message)

                    # Play the default Windows notification sound
                    winsound.PlaySound("SystemNotification", winsound.SND_ALIAS)

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

async def main():
    await recognize_voice()

if __name__ == "__main__":
    asyncio.run(main())
