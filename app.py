from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from pydub import AudioSegment
import os
import moviepy.editor as mp
from openai import OpenAI
from pytubefix import YouTube
from pytubefix.cli import on_progress
from dotenv import load_dotenv

app = Flask(__name__)

# Initialize recognizer
r = sr.Recognizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    video_url = request.form.get('video_url')
    video_file = request.files.get('video_file')  # Handle uploaded video file

    # Convert video_url to string
    video_url = str(video_url) if video_url is not None else ""

    if not video_url and not video_file:  # Check if both video_url and video_file are empty or None
        return jsonify({"error": "No video URL or file provided"}), 400

    try:
        if video_file:  # If a video file is uploaded
            audio_file = 'static/videos/uploaded_audio.mp4'
            video_file.save(audio_file)  # Save the uploaded file
        else:  # If a video URL is provided
                    # Define the output file name
            yt = YouTube(video_url, on_progress_callback = on_progress)
            audio_file = yt.streams.filter(file_extension='mp4').first().download('static/videos/', filename='uploaded_audio.mp4')
        # Call the transcribe_video function
        transcriptions = transcribe_video(audio_file)
        # Prepare messages for ChatGPT
        messages = [{'role': 'user', 'content': 'Summarize the content below as point form for study: ' + ' '.join([text for _, text, _ in transcriptions])}]
        gpt_response = gpt_35_api(messages)
        # Render the result.html template with the transcription data
        return render_template('result.html', transcriptions=transcriptions, gpt_response=gpt_response)

    except Exception as e:
        return jsonify({"Custom Error": str(e)}), 500

def transcribe_video(audio_file):
    """Extract audio from video and transcribe it."""
    # Extract audio from the video
    video = mp.VideoFileClip(audio_file)  # Load the saved video file
    extracted_audio_file = 'static/extracted_audio.wav'  # Define the name for the extracted audio file
    video.audio.write_audiofile(extracted_audio_file, codec='pcm_s16le')  # Save as WAV format

    # Load the audio file for processing
    audio = AudioSegment.from_file(extracted_audio_file)  # Load the extracted audio file
    duration = len(audio) / 1000  # Duration in seconds

    timestamps = []
    with sr.AudioFile(extracted_audio_file) as source:  # Use extracted audio file directly
        for i in range(0, int(duration), 10):  # Process in chunks of 10 seconds
            audio_segment = audio[i * 1000:(i + 10) * 1000]  # Get 10 seconds of audio
            audio_segment.export("temp.wav", format="wav")  # Export to temporary file
            with sr.AudioFile("temp.wav") as temp_source:
                audio_data = r.record(temp_source)
                try:
                    text = r.recognize_google(audio_data)
                    snapshot_filename = capture_snapshot(video,i)  # Capture snapshot at timestamp
                    timestamps.append((i, text, snapshot_filename))  # Store timestamp, text, and snapshot filename
                except sr.UnknownValueError:
                    continue  # Skip if speech is unintelligible
                except sr.RequestError as e:
                    return jsonify({"error": f"Could not request results from Google Speech Recognition service; {e}"}), 500

    # Clean up temporary files
    os.remove(extracted_audio_file)
    if os.path.exists("temp.wav"):
        os.remove("temp.wav")

    return timestamps

# Function to capture a snapshot of the video at a given timestamp
def capture_snapshot(video,timestamp):
    frame = video.get_frame(timestamp)  # Get the frame at the specified timestamp
    snapshot_filename = f"static/images/snapshot_{timestamp}.png"  # Ensure the snapshot is saved in the static folder
    mp.ImageClip(frame).save_frame(snapshot_filename)  # Save the frame as an image
    return snapshot_filename

load_dotenv()
APIKEY = os.getenv("APIKEY")
client = OpenAI(api_key=APIKEY, base_url="https://api.chatanywhere.tech/v1")

def gpt_35_api(messages: list):
    """Generate a response from ChatGPT for the provided messages."""
    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    response = completion.choices[0].message.content
    
    # Remove "- " from the start of each line
    cleaned_response = "\n".join(line.replace("- ", "") for line in response.splitlines())
    
    return cleaned_response

if __name__ == '__main__':
    app.run(debug=True)
