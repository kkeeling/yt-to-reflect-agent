import os
import sys
import json
import requests

def download_youtube_video(url, output_path):
    """
    Downloads a YouTube video using youtube-dl.
    """
    os.system(f"youtube-dl -o {output_path} {url}")

def upload_to_reflect(video_path, reflect_api_url, api_key):
    """
    Uploads a video to Reflect using their API.
    """
    with open(video_path, 'rb') as video_file:
        files = {'file': video_file}
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.post(reflect_api_url, files=files, headers=headers)
        return response.json()

def main(youtube_url, reflect_api_url, api_key, output_path):
    """
    Main function to download a YouTube video and upload it to Reflect.
    """
    download_youtube_video(youtube_url, output_path)
    response = upload_to_reflect(output_path, reflect_api_url, api_key)
    print(json.dumps(response, indent=4))

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python yt-to-reflect-agent.py <youtube_url> <reflect_api_url> <api_key> <output_path>")
        sys.exit(1)

    youtube_url = sys.argv[1]
    reflect_api_url = sys.argv[2]
    api_key = sys.argv[3]
    output_path = sys.argv[4]

    main(youtube_url, reflect_api_url, api_key, output_path)
