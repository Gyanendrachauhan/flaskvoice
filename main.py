import os
from flask import Flask, render_template, request, jsonify
from gtts import gTTS
import openai
import speech_recognition as sr
import base64,tempfile
from decouple import config


app = Flask(__name__)
openai.api_key = config('openai.api_key')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process_audio', methods=['POST'])
# Inside the process_audio route
def process_audio():
    try:
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print("Listening...")
            audio_data = recognizer.listen(source, timeout=10)  # Adjust the timeout as needed

        text_input = recognize_audio(recognizer, audio_data)
        if text_input:
            openai_response = send_text_to_openai(text_input)
            if openai_response:
                audio_response = text_to_voice(openai_response)
                return jsonify({"success": True, "audio_response": audio_response, "recognized_text": text_input, "response_text": openai_response})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    return jsonify({"success": False, "error": "Unable to process audio."})


def recognize_audio(recognizer, audio_data):
    try:
        text_input = recognizer.recognize_google(audio_data)
        return text_input
    except sr.UnknownValueError:
        return ""


def send_text_to_openai(text_input):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=text_input,
        max_tokens=50  # Adjust as needed
    )
    return response.choices[0].text


def text_to_voice(text_response):
    tts = gTTS(text=text_response, lang='en')

    # Save the audio to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_audio:
        tts.save(temp_audio.name)
        temp_audio.seek(0)  # Reset file pointer

        # Read and encode the audio file content to base64
        audio_base64 = base64.b64encode(temp_audio.read()).decode()

    return audio_base64

if __name__ == '__main__':
    app.run(debug=True)
