import os
import sys
import json
import requests
import yt_dlp
from tqdm import tqdm
from colorama import Fore, Style, init

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

    with tqdm(total=100, desc="Downloading and processing", bar_format="{l_bar}{bar} [ time left: {remaining} ]") as pbar:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract information about the YouTube video
            info_dict = ydl.extract_info(url, download=True)
            # Prepare the filename for the downloaded audio
            filename = ydl.prepare_filename(info_dict)
            pbar.update(100)

    # Change the extension to m4a
    new_filename = os.path.splitext(filename)[0] + ".m4a"
    return os.path.abspath(new_filename)

def remove_downloaded_file(filepath):
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
