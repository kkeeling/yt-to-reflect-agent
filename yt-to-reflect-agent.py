import os
import sys
import json
import requests
import yt_dlp
from colorama import Fore, Style, init
from halo import Halo
import whisper

init(autoreset=True)

def agent_output(message):
    print(Fore.GREEN + "(AGENT) -> " + message + Style.RESET_ALL)

def error_output(message):
    print(Fore.RED + "(AGENT) -> " + message + Style.RESET_ALL)

def download_audio_file(url):
    # Download the audio from the YouTube video
    ydl_opts = {
        # Specify the format to download the best audio available
        'format': 'bestaudio/best',
        # Set the output template for the downloaded file
        'outtmpl': '%(title)s.%(ext)s',
        # Use FFmpeg to extract audio and convert it to m4a format
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],
        'quiet': True,
        'no_warnings': True
    }

    spinner = Halo(text='Downloading audio', spinner='dots')
    spinner.start()
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract information about the YouTube video
            info_dict = ydl.extract_info(url, download=True)
            # Prepare the filename for the downloaded audio
            filename = ydl.prepare_filename(info_dict)
    finally:
        spinner.stop()

    # Change the extension to m4a
    new_filename = os.path.splitext(filename)[0] + ".m4a"
    return os.path.abspath(new_filename)

def transcribe_audio(filepath):
    "Transcribe the audio file using Whisper"
    spinner = Halo(text='Transcribing audio', spinner='dots')
    spinner.start()
    
    try:
        model = whisper.load_model("base")
        result = model.transcribe(filepath)
    finally:
        spinner.stop()
    
    return result['text']

def remove_downloaded_file(filepath):
    "Remove the downloaded file from the filesystem"
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        error_output(f"The file {filepath} does not exist.")
    "Remove the downloaded file from the filesystem"
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        error_output(f"The file {filepath} does not exist.")

def upload_to_reflect():
   pass

def main(url):
    # Download the audio file
    downloaded_file = download_audio_file(url)
    agent_output(f"(AGENT) -> Downloaded file: {downloaded_file}")

    # Transcribe the audio file
    transcription = transcribe_audio(downloaded_file)
    agent_output(f"(AGENT) -> Transcription: {transcription}")

    # Remove the downloaded file from the filesystem
    remove_downloaded_file(downloaded_file)
    agent_output(f"(AGENT) -> Removed downloaded file: {downloaded_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        youtube_url = input(Fore.YELLOW + "(AGENT) <- Please enter the YouTube URL: " + Style.RESET_ALL)
        agent_output(f"(AGENT) -> Received YouTube URL: {youtube_url}")
    else:
        youtube_url = sys.argv[1]
    main(youtube_url)
