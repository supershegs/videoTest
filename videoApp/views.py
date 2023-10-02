import os
import moviepy.editor as mp
import speech_recognition as sr
import openai
import requests
# from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import status
from rest_framework.parsers import FileUploadParser, MultiPartParser

from .savechunks import *
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

class VideoChunkUploadView(APIView):
    parser_classes = (MultiPartParser,)
    def post(self, request, format=None):
        print('Printed data/file received before any processing: ',request.data)
        blob_type = request.data.get('type', '')
        if 'video/mp4' in blob_type or 'video/webm' in blob_type:
            # Handle video chunks
            print('Printed file sent if video/mp4 or video/webm', request.data)
            serializer = VideoChunkSerializer(data=request.data)
            if serializer.is_valid():
                video_chunk_instance = serializer.save()

                # Convert video chunk to audio
                video_path = video_chunk_instance.video_chunk.path
                audio_path = os.path.splitext(video_path)[0] + ".wav"

                video_clip = mp.VideoFileClip(video_path)
                audio_clip = video_clip.audio
                audio_clip.write_audiofile(audio_path)
                # Transcribe audio to manuscript
                try:
                    with open(audio_path, "rb") as audio_file: 
                        print(audio_file)
                        manuscript = openai.Audio.transcribe("whisper-1", audio_file)
                except FileNotFoundError:
                    return Response("Audio file not found")
                except requests.exceptions.RequestException as e:
                    return Response(f"Error making a request to OpenAI API: {e}",status=status.HTTP_400_BAD_REQUEST)
                except openai.OpenAIError as e:
                    return Response(f"OpenAI API error: {e}", status=status.HTTP_402_PAYMENT_REQUIRED)
                except openai.error.AuthenticationError as e:
                    return Response(f"OpenAI authentication error: {e}", status=status.HTTP_401_UNAUTHORIZED)
                except openai.error.APIError as e:
                    return Response(f"OpenAI API error: {e}",status=status.HTTP_408_REQUEST_TIMEOUT)        
            else:
                return Response("content type not accepted", status=status.HTTP_406_NOT_ACCEPTABLE)
        elif 'application/octet-stream' in blob_type:
            # Handle binary chunks
            print('Printed file sent if octet-stream', request.data)
            chunk = request.data
            chunk_number = request.POST.get('chunk_number')
            file_id = request.POST.get('file_id')  # Identifier for the complete file
            save_chunk_to_temporary_location(file_id, chunk_number, chunk)
            if all_chunks_received(file_id):
                assemble_file(file_id)
            return Response("Chunk received and processed", status=status.HTTP_200_OK)
        elif request.data != '':
            serializer = VideoChunkSerializer(data=request.data)
            if serializer.is_valid():
                video_chunk_instance = serializer.save()# Save the video chunk to the 'media/chunks/' directory
                
                video_path = video_chunk_instance.video_chunk.path 
                print(video_path)
                # audio_path = os.path.splitext(video_path)[0] + ".wav"  # Change the audio format to WAV
                audio_path = os.path.splitext(video_path)[0] + ".mp3"
    
                
                video_clip = mp.VideoFileClip(video_path)
                
                audio_clip = video_clip.audio
                audio_clip.write_audiofile(audio_path)
                
                try:
                    with open(audio_path, "rb") as audio_file: 
                        print(audio_file)
                        manuscript = openai.Audio.transcribe("whisper-1", audio_file)
                except FileNotFoundError:
                    return Response("Audio file not found")
                except requests.exceptions.RequestException as e:
                    return Response(f"Error making a request to OpenAI API: {e}",status=status.HTTP_400_BAD_REQUEST)
                except openai.OpenAIError as e:
                    return Response(f"OpenAI API error: {e}", status=status.HTTP_402_PAYMENT_REQUIRED)
                except openai.error.AuthenticationError as e:
                    return Response(f"OpenAI authentication error: {e}", status=status.HTTP_401_UNAUTHORIZED)
                except openai.error.APIError as e:
                    return Response(f"OpenAI API error: {e}",status=status.HTTP_408_REQUEST_TIMEOUT)
            else:
                return Response("content type not accepted", status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            # Handle unsupported content type
            print('Printed file sent if not supported content type', request.data)
            return Response("Unsupported content type", status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        # Update the video chunk instance with the manuscript
        video_chunk_instance.manuscript = manuscript
        video_chunk_instance.save()

        return Response(VideoChunkSerializer(video_chunk_instance).data, status=status.HTTP_201_CREATED)
