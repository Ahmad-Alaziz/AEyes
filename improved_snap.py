import os
import base64
import requests
import json
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library


GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)




api_key = os.getenv("API_KEY")

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "/home/pi/img/image.jpeg"

# Getting the base64 string
base64_image = encode_image(image_path)

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

payload = {
  "model": "gpt-4-vision-preview",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What’s in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
          }
        }
      ]
    }
  ],
  "max_tokens": 300
}



# Function to convert text to speech using the ElevenLabs API
def convert_text_to_speech(message, voice):
    api_key = 'ELEVEN_LABS_KEY_HERE'
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/stream?optimize_streaming_latency=1"

    headers = {
        'accept': 'audio/mpeg',
        'Content-Type': 'application/json',
        'xi-api-key': api_key,
    }

    payload = {
        'text': message,
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.ok:
        # Save the audio stream to a file
        file_path = '/home/pi/audio.mp3'
        with open(file_path, 'wb') as audio_file:
            audio_file.write(response.content)
        print(f"The audio was saved as {file_path}.")
        return file_path
    else:
        # Handle errors
        print(f"Error: {response.status_code}")
        print(f"Message: {response.json()}")
        return None

# Example usage
# Replace 'your_message_here' with your actual message and 'voice_id' with the voice you want to use.
#audio_file_path = convert_text_to_speech(text, '21m00Tcm4TlvDq8ikWAM')

#cmd = 'paplay audio.mp3'
#os.system(cmd)


while True: # Run forever
    if GPIO.input(10) == GPIO.LOW:
        print("Button was pushed!")
        cmd = '/home/pi/image.sh .'
        os.system(cmd)

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        text = (response.json()['choices'][0]['message']['content'])

        audio_file_path = convert_text_to_speech(text, '21m00Tcm4TlvDq8ikWAM')

        cmd = 'paplay audio.mp3'
        os.system(cmd)

