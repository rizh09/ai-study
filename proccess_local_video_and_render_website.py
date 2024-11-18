import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment
import os

# ------------------------------
# Video and Audio Processing
# ------------------------------

# Load the video
video = mp.VideoFileClip("demo.mp4")

# Extract the audio from the video
audio_file = video.audio
audio_file.write_audiofile("demo.wav")

# Initialize recognizer
r = sr.Recognizer()

# Load the audio file
audio = AudioSegment.from_wav("demo.wav")
duration = len(audio) / 1000  # Duration in seconds

# Function to capture a snapshot of the video at a given timestamp
def capture_snapshot(timestamp):
    frame = video.get_frame(timestamp)  # Get the frame at the specified timestamp
    snapshot_filename = f"snapshot_{timestamp}.png"
    mp.ImageClip(frame).save_frame(snapshot_filename)  # Save the frame as an image
    return snapshot_filename

# ------------------------------
# Transcription Process
# ------------------------------

# Function to transcribe audio with timestamps
def transcribe_audio_with_timestamps(audio_file):
    timestamps = []
    with sr.AudioFile(audio_file) as source:
        for i in range(0, int(duration), 10):  # Process in chunks of 10 seconds
            audio_segment = audio[i * 1000:(i + 10) * 1000]  # Get 10 seconds of audio
            audio_segment.export("temp.wav", format="wav")  # Export to temporary file
            with sr.AudioFile("temp.wav") as temp_source:
                audio_data = r.record(temp_source)
                try:
                    text = r.recognize_google(audio_data)
                    snapshot_filename = capture_snapshot(i)  # Capture snapshot at timestamp
                    timestamps.append((i, text, snapshot_filename))  # Store timestamp, text, and snapshot filename
                except sr.UnknownValueError:
                    continue  # Skip if speech is unintelligible
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
    return timestamps

# Transcribe the audio and get timestamps
transcriptions = transcribe_audio_with_timestamps("demo.wav")
# print("\n transcriptions : ",transcriptions)  # Removed unnecessary print statement
# ------------------------------
# ChatGPT Interaction
# ------------------------------
APIKEY = os.getenv("APIKEY")
client = OpenAI(api_key=APIKEY, base_url="https://api.chatanywhere.tech/v1")

def gpt_35_api(messages: list):
    """Generate a response from ChatGPT for the provided messages."""
    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    return completion.choices[0].message.content

# Prepare messages for ChatGPT
messages = [{'role': 'user', 'content': 'Summarize the content below as point form for study: ' + ' '.join([text for _, text, _ in transcriptions])}]
gpt_response = gpt_35_api(messages)

# print the ChatGPT response
# print("\nChatGPT Response:\n", gpt_response)  # Removed unnecessary print statement
# ------------------------------
# Clean Up Temporary Files
# ------------------------------

# Clean up temporary files
os.remove("demo.wav")
if os.path.exists("temp.wav"):
    os.remove("temp.wav")

# ------------------------------
# Generate HTML for Transcriptions
# ------------------------------

# Generate HTML for transcriptions
transcriptions_html = ""
for timestamp, text, snapshot in transcriptions:
    transcriptions_html += f'<div class="transcription"><span class="timestamp" onclick="jumpToTimestamp({timestamp})">{timestamp}s</span>: <span id="text-{timestamp}">{text}</span><br><img src="{snapshot}" alt="Snapshot at {timestamp}s" width="200"></div>\n'

# Save the HTML to a file
with open("index.html", "w") as f:
    f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transcription Viewer</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        h1 {{
            text-align: center;
            color: #333;
        }}
        .container {{
            display: flex; /* Use flexbox for horizontal alignment */
            justify-content: space-between; /* Space between items */
            align-items: stretch; /* Stretch items to the same height */
            width: 100%;
            max-width: 1200px;
        }}
        .video-container {{
            flex: 1;
            margin-right: 20px;
        }}
        video {{
            display: block;
            width: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}
        .timestamp {{
            color: #007BFF;
            cursor: pointer;
            font-weight: bold;
        }}
        .chatgpt-response {{
            flex: 1; /* Allow the ChatGPT response to take available space */
            margin-right: 20px; /* Add some space to the right */
        }}
        .chatgpt-response h2 {{
            margin: 0 0 10px;
            color: #333;
        }}
        .chatgpt-response ul {{
            list-style-type: disc; /* Use bullet points */
            padding-left: 20px; /* Indent the list */
            margin: 0; /* Remove default margin */
        }}
        .chatgpt-response li {{
            margin-bottom: 5px; /* Space between list items */
            color: #555; /* Text color for list items */
        }}
        button {{
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            background-color: #007BFF;
            color: white;
            cursor: pointer;
        }}
        button:hover {{
            background-color: #0056b3;
        }}
        @media (max-width: 600px) {{
            body {{
                padding: 10px;
            }}
            .container {{
                flex-direction: column; /* Stack elements vertically on small screens */
            }}
            .video-container {{
                margin-right: 0; /* Remove margin on small screens */
                margin-bottom: 20px; /* Add space below video */
            }}
            video {{
                width: 100%; /* Ensure video is responsive */
            }}
        }}
        .chatgpt-response-wrapper {{
            background: white; /* Background for the ChatGPT response */
            border-radius: 8px; /* Rounded corners */
            padding: 15px; /* Padding inside the box */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Shadow for depth */
            flex: 1; /* Allow the wrapper to take available space */
            margin: 10px 10px 0px 0px;
            display: flex; /* Use flexbox for vertical alignment */
            flex-direction: column; /* Stack children vertically */
            height: 100%; /* Ensure both containers take full height */
            max-height: 600px;
            min-height: 600px;
        }}
            
        .transcription {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 10px 0px 0px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            max-height: 600px;
            overflow-y: auto; /* Enable scrolling if content overflows */
            flex: 1;
        }}
    </style>
</head>
<body>
    <h1>Transcriptions with Timestamps</h1>
    
    <div class="container">
        <div class="video-container">
            <!-- Video Element -->
            <video id="transcriptionVideo" width="640" height="360" controls>
                <source src="demo.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
    </div>

    <!-- Space for ChatGPT Response and Transcriptions -->
    <div class="container">
        <div class="chatgpt-response-wrapper">
            <h2>ChatGPT Response:</h2>
            <ul id="chatgptResponseList">
                {''.join(f'<li>{point.strip()}</li>' for point in gpt_response.splitlines() if point.strip())}
            </ul>
        </div>

        <div class="transcription">
            <div id="transcriptions">
                {transcriptions_html}
            </div>
        </div>
    </div>

    <script>
        // Function to jump to the corresponding timestamp in the video
        function jumpToTimestamp(timestamp) {{
            const video = document.getElementById('transcriptionVideo');
            video.currentTime = timestamp; // Set the video time to the timestamp
            video.play(); // Optionally play the video
        }}

    </script>
</body>
</html>""")
