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
from .mytranscribe import audiotranscribe

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
                manuscript =audiotranscribe(audio_path)    
                if manuscript:
                    video_chunk_instance.manuscript = manuscript
                    video_chunk_instance.save()
                    print(video_chunk_instance)
                    result = {
                        'video_id':video_chunk_instance.id,
                        'manuscript': video_chunk_instance.manuscript,
                        'video_path': video_path
                    }
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    return Response("Transcription failed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                   
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
           
                # audio_path = os.path.splitext(video_path)[0] + ".wav"  # Change the audio format to WAV
                audio_path = os.path.splitext(video_path)[0] + ".mp3"
                
                video_clip = mp.VideoFileClip(video_path)
                
                audio_clip = video_clip.audio
                audio_clip.write_audiofile(audio_path)

                manuscript =audiotranscribe(audio_path)    
                if manuscript:
                    video_chunk_instance.manuscript = manuscript
                    video_chunk_instance.save()
                    print(video_chunk_instance)
                    result = {
                        'video_id':video_chunk_instance.id,
                        'manuscript': video_chunk_instance.manuscript,
                        'video_path': video_path
                    }
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    return Response("Transcription failed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response("content type not accepted", status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            # Handle unsupported content type
            print('Printed file sent if not supported content type', request.data)
            return Response("Unsupported content type", status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        #