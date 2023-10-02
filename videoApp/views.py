import os
import moviepy.editor as mp
import speech_recognition as sr
# from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import status
from rest_framework.parsers import FileUploadParser, MultiPartParser

from .savechunks import *


class VideoChunkUploadView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, format=None):
        print(request.data)
        blob_type = request.data.get('type', '')
        if 'video/mp4' in blob_type or 'video/webm' in blob_type:
            # Handle video chunks
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
                recognizer = sr.Recognizer()
                with sr.AudioFile(audio_path) as source:
                    audio = recognizer.record(source)
                    try:
                        manuscript = recognizer.recognize_google(audio)
                    except sr.RequestError as e:
                        return Response("Could not request results from Google Speech Recognition service; {0}".format(e), status=status.HTTP_400_BAD_REQUEST)
                    except sr.UnknownValueError:
                        manuscript = "Google Speech Recognition could not understand audio"

                # Update the video chunk instance with the manuscript
                video_chunk_instance.manuscript = manuscript
                video_chunk_instance.save()

                return Response(VideoChunkSerializer(video_chunk_instance).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class VideoChunkUploadView(APIView):
#     parser_classes = (MultiPartParser,)

#     def post(self, request, format=None):
#         print(request.data)
#         if request.data.content_type == 'video/mp4' or request.data.content_type == 'video/webm':
#             serializer = VideoChunkSerializer(data=request.data)
#             if serializer.is_valid():
#                 video_chunk_instance = serializer.save()

#                 # Convert video chunk to audio
#                 video_path = video_chunk_instance.video_chunk.path
#                 audio_path = os.path.splitext(video_path)[0] + ".wav"

#                 video_clip = mp.VideoFileClip(video_path)
#                 audio_clip = video_clip.audio
#                 audio_clip.write_audiofile(audio_path)

#                 # Transcribe audio to manuscript
#                 recognizer = sr.Recognizer()
#                 with sr.AudioFile(audio_path) as source:
#                     audio = recognizer.record(source)
#                     try:
#                         manuscript = recognizer.recognize_google(audio)
#                     except sr.RequestError as e:
#                         return Response("Could not request results from Google Speech Recognition service; {0}".format(e), status=status.HTTP_400_BAD_REQUEST)
#                     except sr.UnknownValueError:
#                         manuscript = "Google Speech Recognition could not understand audio"

#                 # Update the video chunk instance with the manuscript
#                 video_chunk_instance.manuscript = manuscript
#                 video_chunk_instance.save()

#                 return Response(VideoChunkSerializer(video_chunk_instance).data, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         elif request.data.content_type == 'application/octet-stream':
#             chunk = request.data
#             chunk_number = request.POST.get('chunk_number')
#             file_id = request.POST.get('file_id')  # Identifier for the complete file
#             save_chunk_to_temporary_location(file_id, chunk_number, chunk)

#             if all_chunks_received(file_id):
#                 assemble_file(file_id)
#             return Response("Chunk received and processed", status=status.HTTP_200_OK)
#         else:
#             return Response("Unsupported content type", status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


# class VideoChunkUploadView(APIView):
    
#     parser_classes = (MultiPartParser,)

#     def post(self, request, format=None):
#         serializer = VideoChunkSerializer(data=request.data)
#         if serializer.is_valid():
#             video_chunk_instance = serializer.save()# Save the video chunk to the 'media/chunks/' directory
#             video_path = video_chunk_instance.video_chunk.path  # Convert video chunk to audio
#             print(video_path)
#             audio_path = os.path.splitext(video_path)[0] + ".wav"  # Change the audio format to WAV
#             # audio_path = os.path.splitext(video_path)[0] + ".mp3"
#             print(audio_path)
#             video_clip = mp.VideoFileClip(video_path)
#             audio_clip = video_clip.audio
#             audio_clip.write_audiofile(audio_path)

#             # Transcribe audio to manuscript
#             recognizer = sr.Recognizer()
#             print(recognizer)
#             with sr.AudioFile(audio_path) as source:
#                 audio = recognizer.record(source)
#                 # manuscript = recognizer.recognize_google(audio)
#                 try:
#                     manuscript = recognizer.recognize_google(audio)
#                     print(manuscript)
#                 except sr.RequestError as e:
#                    return Response("Could not request results from Google Speech Recognition service; {0}".format(e))
#                 except sr.UnknownValueError:
#                     print("Google Speech Recognition could not understand audio")


#             # Update the video chunk instance with the manuscript
#             video_chunk_instance.manuscript = manuscript
#             video_chunk_instance.save()

#             return Response(VideoChunkSerializer(video_chunk_instance).data, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

