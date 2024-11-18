from flask import Flask, render_template, request, jsonify, send_from_directory
import speech_recognition as sr
from pydub import AudioSegment
import os
import moviepy.editor as mp
from openai import OpenAI
from pytubefix import YouTube
from pytubefix.cli import on_progress
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import mimetypes
from pdf2image import convert_from_path  # Import pdf2image to convert PDF pages to images

app = Flask(__name__)

# Initialize recognizer
r = sr.Recognizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    video_url = request.form.get('video_url')
    # Convert video_url to string
    video_url = str(video_url) if video_url is not None else ""

    if not video_url : # Check if all inputs are empty or None
        return jsonify({"error": "No video URL, file, or PDF provided"}), 400

    try:
        # If a video URL is provided
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
    print("before")
    print(response)
    # Remove "- " from the start of each line
    cleaned_response = "\n".join(line.replace("- ", "") for line in response.splitlines())
    print("after")
    print(cleaned_response)
    return cleaned_response

def read_pdf_and_capture_images(pdf_file):
    """Extract text from a PDF file and capture images of each page."""
    reader = PdfReader(pdf_file)  # Create a PdfReader object
    text_and_images = []  # List to hold tuples of (page_number, text, image_path)

    # Convert PDF pages to images
    images = convert_from_path(pdf_file)

    for page_number, page in enumerate(reader.pages):
        text = page.extract_text()  # Extract text from the page
        image_path = f"static/images/snapshot_{page_number + 1}.png"  # Define image path
        images[page_number].save(image_path, 'PNG')  # Save the image of the page

        text_and_images.append((page_number + 1, text, image_path))  # Store page number, text, and image path

    return text_and_images  # Return the list of tuples

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files.get('file')  # Assuming the input field name is 'file'
    
    if uploaded_file is None:
        return jsonify({"Custom Error": "No file uploaded."}), 400

    file_extension = uploaded_file.filename.rsplit('.', 1)[-1].lower()  # Get the file extension

    if file_extension == 'pdf' or file_extension == 'application/pdf':  # If a PDF file is uploaded
        # Save the uploaded PDF file to a temporary location
        pdf_file_path = 'static/uploads/uploaded_file.pdf'
        uploaded_file.save(pdf_file_path)  # Save the uploaded file
        text_and_images = read_pdf_and_capture_images(pdf_file_path)  # Read text and capture images
        gpt_responses = []  # List to hold responses for each page

        for page_number, page_text, image_path in text_and_images:
            messages = [{'role': 'user', 'content': f'Please summarize the content below in point form for study (Page {page_number}): {page_text}'}]
            gpt_response = gpt_35_api(messages)
            gpt_responses.append((page_number, gpt_response, image_path))  # Store page number, response, and image path

        print(gpt_responses)
        return render_template('result_pdf.html', transcriptions=[], gpt_response=gpt_responses)

    elif file_extension in ['mp4', 'mov', 'avi', 'mkv'] or file_extension.startswith('video/'):  # If a video file is uploaded
        audio_file = 'static/videos/uploaded_audio.mp4'
        uploaded_file.save(audio_file)  # Save the uploaded file
        # Process the video file as needed
        transcriptions = transcribe_video(audio_file)
        # Prepare messages for ChatGPT
        messages = [{'role': 'user', 'content': 'Summarize the content below as point form for study: ' + ' '.join([text for _, text, _ in transcriptions])}]
        gpt_response = gpt_35_api(messages)
        # Render the result.html template with the transcription data
        return render_template('result.html', transcriptions=transcriptions, gpt_response=gpt_response)

    else:
         return jsonify({"Custom Error": "Unsupported file type. Please upload a PDF or video file."}), 400

@app.route('/pdf/<path:filename>')
def pdf_view(filename):
    return send_from_directory('', filename)

if __name__ == '__main__':
    app.run(debug=True)
