from flask import Flask, render_template, request
import speech_recognition as sr
from pydub import AudioSegment
import os
from pytube import YouTube
import io
import requests

app = Flask(__name__)

# Initialize recognizer
r = sr.Recognizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    video_url = request.form['video_url']
    
    # Download the YouTube video stream
    try:
        yt = YouTube(video_url)
        video_stream = yt.streams.filter(only_audio=True).first()  # Get the audio stream
        audio_url = video_stream.url  # Get the direct audio URL
        print(f"Audio URL: {audio_url}")  # Debugging statement
    except Exception as e:
        return render_template('result.html', transcriptions=[], error=str(e))

    # Stream the audio into memory
    try:
        response = requests.get(audio_url)
        audio_data = io.BytesIO(response.content)
        audio = AudioSegment.from_file(audio_data, format="mp4")  # Assuming the audio is in mp4 format
        print(f"Audio Duration: {len(audio) / 1000} seconds")  # Debugging statement
    except Exception as e:
        return render_template('result.html', transcriptions=[], error=str(e))

    duration = len(audio) / 1000  # Duration in seconds

    # Function to transcribe audio with timestamps
    def transcribe_audio_with_timestamps(audio):
        timestamps = []
        for i in range(0, int(duration), 10):  # Process in 10-second segments
            audio_segment = audio[i * 1000:(i + 10) * 1000]
            audio_segment.export("temp.wav", format="wav")  # Export segment to a temporary file
            print(f"Processing segment: {i} to {i + 10} seconds")  # Debugging statement
            with sr.AudioFile("temp.wav") as temp_source:
                audio_data = r.record(temp_source)
                try:
                    text = r.recognize_google(audio_data)
                    timestamps.append((i, text))  # Append timestamp and transcribed text
                    print(f"Transcribed: {text}")  # Debugging statement
                except sr.UnknownValueError:
                    print("Could not understand audio")  # Debugging statement
                    continue  # Skip if audio is not understood
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
        return timestamps

    # Transcribe the audio and get timestamps
    transcriptions = transcribe_audio_with_timestamps(audio)

    # Clean up temporary files
    if os.path.exists("temp.wav"):
        os.remove("temp.wav")

    return render_template('result.html', transcriptions=transcriptions)

if __name__ == '__main__':
    app.run(debug=True)
