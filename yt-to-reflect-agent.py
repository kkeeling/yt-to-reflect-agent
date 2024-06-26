import os
import sys
import yt_dlp
import io
import json
from colorama import Fore, Style, init
from halo import Halo
from pydub import AudioSegment
from dotenv import load_dotenv
import llm
from chain import MinimalChainable
from openai import OpenAI
import requests
from datetime import datetime

init(autoreset=True)

def agent_output(message):
    print(Fore.GREEN + "(AGENT) -> " + message + Style.RESET_ALL)

def error_output(message):
    print(Fore.RED + "(AGENT) -> " + message + Style.RESET_ALL)

def build_models():
    load_dotenv()

    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    sonnet_3_5_model: llm.Model = llm.get_model("claude-3.5-sonnet")
    sonnet_3_5_model.key = ANTHROPIC_API_KEY

    return sonnet_3_5_model


def prompt(model: llm.Model, prompt: str):
    res = model.prompt(
        prompt,
        temperature=0.5,
    )
    return res.text()


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
            # Write info_dict to file, with pretty json

            title = info_dict['title']
            description = info_dict['description']

            # Prepare the filename for the downloaded audio
            filename = ydl.prepare_filename(info_dict)
    finally:
        spinner.stop()

    # Change the extension to m4a
    new_filename = os.path.splitext(filename)[0] + ".m4a"

    return {
        "title": title,
        "description": description,
        "filepath": os.path.abspath(new_filename)
    }


def transcribe_audio(filepath):
    "Transcribe the audio file using OpenAI's Whisper API"
    spinner = Halo(text='Transcribing audio', spinner='dots')
    
    try:
        # Load the audio file using AudioSegment
        audio = AudioSegment.from_file(filepath)
        agent_output("Audio file loaded successfully.")

        # Define chunk duration (20 minutes)
        chunk_duration_ms = 20 * 60 * 1000  # 20 minutes in milliseconds

        # Split audio into chunks
        chunks = [audio[i:i + chunk_duration_ms] for i in range(0, len(audio), chunk_duration_ms)]

        spinner.start()

        client = OpenAI()
        transcription = ""
        for i, chunk in enumerate(chunks):
            try:
                # agent_output(f"Transcribing chunk {i + 1} of {len(chunks)}")
                file_obj = io.BytesIO(chunk.export(format="mp3").read())
                file_obj.name = f"audio_chunk_{i}.mp3"

                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=file_obj
                )
                transcription += response.text + " "
            except Exception as e:
                error_output(f"Error transcribing chunk {i + 1} of {len(chunks)}: {e}")
                break

    finally:
        spinner.stop()
    
    return transcription


def run_chainable(transcription, title, description):
    # Load the summarize prompt
    with open("summarize_prompt.md", "r") as f:
        summarize_prompt = f.read()

    # Load the decorate prompt
    with open("decorate_prompt.md", "r") as f:
        decorate_prompt = f.read()

    spinner = Halo(text='Summarizing...', spinner='dots')

    try:
        model = build_models()

        result, context_filled_prompts = MinimalChainable.run(
        context={"title": title, "description": description, "transcript": transcription},
        model=model,
        callable=prompt,
        prompts=[
            # prompt 1
            f"{summarize_prompt}",
            # prompt 2
            f"{decorate_prompt}"
        ])
    finally:
        spinner.stop()
    
    return result

def remove_downloaded_file(filepath):
    "Remove the downloaded file from the filesystem"
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        error_output(f"The file {filepath} does not exist.")

def add_note_to_reflect(title, content):
    """
    Adds a new note to Reflect using their API.
    
    Args:
    title (str): The title of the new note
    content (str): The content of the new note
    
    Returns:
    dict: The response from the API containing the created note's details
    """
    
    # API endpoint for creating a new note
    url = f"https://reflect.app/api/graphs/{os.getenv('REFLECT_GRAPH_ID')}/notes"

    # Get the API key from the environment
    api_key = os.getenv("REFLECT_API_KEY")
    
    # Headers for the request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Payload for creating a new note
    payload = {
        "subject": title,
        "content_markdown": content,
        "pinned": False
    }
    
    try:
        # Send POST request to create a new note
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Return the created note's details
        return response.json()
    
    except requests.exceptions.RequestException as e:
        error_output(f"An error occurred: {e}")
        return None

def create_reflect_note(url, title, description, summary, transcription):
    """
    Creates a new note in Reflect with the given details.
    
    Args:
    url (str): The URL of the YouTube video
    title (str): The title of the new note
    description (str): The description of the new note
    summary (str): The summarized response from the agent
    transcription (str): The transcription of the audio
    
    Returns:
    dict: The response from the API containing the created note's details
    """
    content = f"""
- Type: #link
- URL: {url}
- Description: {description}
- Summary:\n\t{summary}
- Raw:\n\t{transcription}
    """

    spinner = Halo(text='Creating note in Reflect...', spinner='dots')
    spinner.start() 

    result = add_note_to_reflect(title, content)

    spinner.stop()

    return result

def append_to_daily_note(content, list_name="Links"):
    """
    Appends content to the daily note in Reflect using their API.
    
    Args:
    content (str): The content to append to the daily note
    list_name (str): The name of the list to append to (default: "Links")
    
    Returns:
    dict: The response from the API containing the updated note's details
    """
    
    # API endpoint for updating the daily note
    url = f"https://reflect.app/api/graphs/{os.getenv('REFLECT_GRAPH_ID')}/daily-notes"
    
    # Get the API key from the environment
    api_key = os.getenv("REFLECT_API_KEY")
    
    # Headers for the request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Get the current date for the daily note
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Payload for updating the daily note
    payload = {
        "date": today,
        "text": content,
        "transform_type": "list-append",
        "list_name": list_name
    }
    
    try:
        # Send PUT request to update the daily note
        response = requests.put(url, headers=headers, json=payload)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Return the updated note's details
        return response.json()
    
    except requests.exceptions.RequestException as e:
        error_output(f"An error occurred: {e}")
        return None

def main(url):
    downloaded_file = None
    try:
        # Download the audio file
        result = download_audio_file(url)
        downloaded_file = result['filepath']
        agent_output(f"Downloaded file: {result['title']}")

        # Transcribe the audio file
        transcription = transcribe_audio(downloaded_file)
        agent_output(f"Transcription of {result['title']} complete.")

        # Run the chainable
        agent_response = run_chainable(transcription, result['title'], result['description'])
        agent_output(f"Summary of {result['title']} complete.")

        # Create a new note in Reflect
        create_reflect_note(url, result['title'], result['description'], agent_response[0], transcription)
        agent_output(f"Note created in Reflect.")
    
        # Append backlink to new note to daily note
        append_to_daily_note(f"- [[{result['title']}]]({url})")
    finally:
        if downloaded_file:
            # Remove the downloaded file from the filesystem
            remove_downloaded_file(downloaded_file)
            agent_output(f"Removed downloaded file: {downloaded_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        youtube_url = input(Fore.YELLOW + "(AGENT) <- Please enter the YouTube URL: " + Style.RESET_ALL)
        agent_output(f"Received YouTube URL: {youtube_url}")
    else:
        youtube_url = sys.argv[1]
    main(youtube_url)
