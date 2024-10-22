import os
from pytubefix import YouTube
from pytubefix.cli import on_progress

def delete_file_if_exists(file_path):
    """Delete the file if it exists."""
    if os.path.exists(file_path):
        os.remove(file_path)  # Delete the file
        print(f"Deleted file: {file_path}")
    else:
        print(f"File does not exist: {file_path}")

def download_youtube_video(video_url, output_path):
    """Download a YouTube video with a custom name."""
    try:
        yt = YouTube(video_url, on_progress_callback = on_progress)
        yt.streams.filter(file_extension='mp4').first().download(output_path, filename='abc.mp4', filename_prefix="test_")
        #https://github.com/JuanBindez/pytubefix/blob/fe2990829053f4603aec9161ec1fd23bb40236ac/pytubefix/streams.py#L292
        
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
video_url = "https://www.youtube.com/watch?v=gXwewPgLmkE"  # Replace with your YouTube video URL
output_path = "static/videos"  # Replace with your desired output path
download_youtube_video(video_url, output_path)
