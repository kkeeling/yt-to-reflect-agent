import os
import sys
import json
import requests
import yt_dlp
from colorama import Fore, Style, init

init(autoreset=True)

def agent_output(message):
    print(Fore.GREEN + message + Style.RESET_ALL)

def error_output(message):
    print(Fore.RED + message + Style.RESET_ALL)
def download_youtube_video(url):
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

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract information about the YouTube video
        info_dict = ydl.extract_info(url, download=True)
        # Prepare the filename for the downloaded audio
        filename = ydl.prepare_filename(info_dict)

    return filename

def remove_downloaded_file(filepath):
    "Remove the downloaded file from the filesystem"
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        error_output(f"The file {filepath} does not exist.")

def upload_to_reflect():
   pass

def main(youtube_url):
    # Download the audio file
    downloaded_file = download_youtube_video(youtube_url)
    agent_output(f"Downloaded file: {downloaded_file}")

    # Remove the downloaded file from the filesystem
    remove_downloaded_file(downloaded_file)



if __name__ == "__main__":
    if len(sys.argv) != 2:
        youtube_url = input(Fore.YELLOW + "(AGENT) Please enter the YouTube URL: " + Style.RESET_ALL)
        agent_output(f"Received YouTube URL: {youtube_url}")
    else:
        youtube_url = sys.argv[1]
    main(youtube_url)
