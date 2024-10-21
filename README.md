# Project Title

## Description
This project utilizes various libraries for video processing, speech recognition, and interaction with the OpenAI API. The main functionality is implemented in `main.py`.

## Prerequisites
Before you begin, ensure you have the following installed on your system:

- Python 3.x
- pip (Python package installer)
- Homebrew (for macOS users, to install ffmpeg)

## Installation

### Step 1: Clone the Repository
Clone this repository to your local machine using:
`
git clone https://github.com/rizh09/ai-interviewr.git
`
`
cd ai-interviewr
`

### Step 2: Install Required Libraries
You can install the required Python libraries using pip. Run the following commands in your terminal:

`
pip install moviepy
`
`
pip install SpeechRecognition
`
`
pip install pydub
`
`
pip install openai
`

### Step 3: Install ffmpeg
`ffmpeg` is required for audio processing. If you are using macOS, you can install it using Homebrew:


brew install ffmpeg


For other operating systems, you can download and install `ffmpeg` from the [official website](https://ffmpeg.org/download.html).

## Usage

### Running the Script
Once you have installed all the necessary libraries, you can run the `main.py` script. Use the following command in your terminal:


`python main.py`


### Configuration
Make sure to configure any necessary API keys or settings in `main.py` before running the script. For example, if you are using the OpenAI API, you will need to set your API key:

`import openai`
`openai.api_key = 'your-api-key-here'`


### Features
- **Video Processing**: The script can process video files using `moviepy`.
- **Speech Recognition**: It can recognize speech from audio files using `SpeechRecognition`.
- **Audio Manipulation**: The script can manipulate audio files using `pydub`.
- **OpenAI Interaction**: It can interact with the OpenAI API for various functionalities.

## Troubleshooting
- If you encounter issues with `ffmpeg`, ensure it is correctly installed and accessible in your system's PATH.
- For any library-related issues, make sure you have the correct versions installed.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- [moviepy](https://zulko.github.io/moviepy/)
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/)
- [pydub](https://github.com/jiaaro/pydub)
- [OpenAI](https://openai.com/)