import os
import sys
import json
import requests
import yt_dlp
from colorama import Fore, Style, init

init(autoreset=True)

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
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract information about the YouTube video
        info_dict = ydl.extract_info(url, download=True)
        # Prepare the filename for the downloaded audio
        filename = ydl.prepare_filename(info_dict)

def upload_to_reflect():
   pass

def main(youtube_url):
    download_youtube_video(youtube_url)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        youtube_url = input(Fore.YELLOW + "(AGENT) Please enter the YouTube URL: " + Style.RESET_ALL)
    else:
        youtube_url = sys.argv[1]
    main(youtube_url)
