import assemblyai as aai
import requests
from rest_framework.response import Response

from rest_framework import status
aai.settings.api_key = f"3c78a774047f44a698694552baa8cf95"

def audiotranscribe(audio_path):
    
    try:
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_path)
        return (transcript.text)
            # manuscript = openai.Audio.transcribe("whisper-1", audio_file)
    except FileNotFoundError:
        return Response("Audio file not found")
    except requests.exceptions.RequestException as e:
        return Response(f"Error making a request to OpenAI API: {e}",status=status.HTTP_400_BAD_REQUEST)
    except aai.error.AuthenticationError as e:
        return Response(f"OpenAI authentication error: {e}", status=status.HTTP_401_UNAUTHORIZED)
    except aai.error.APIError as e:
        return Response(f"OpenAI API error: {e}",status=status.HTTP_408_REQUEST_TIMEOUT)