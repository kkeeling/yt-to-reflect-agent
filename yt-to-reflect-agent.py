import os
import sys
import json
import requests

def download_youtube_video(url, output_path):
   pass

def upload_to_reflect(video_path, reflect_api_url, api_key):
   pass

def main(youtube_url):
    pass

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python yt-to-reflect-agent.py <youtube_url>")
        sys.exit(1)
        
    youtube_url = sys.argv[1]
    main(youtube_url)
