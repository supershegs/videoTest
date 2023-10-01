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


class VideoChunkUploadView(APIView):
    
    parser_classes = (MultiPartParser,)

    def post(self, request, format=None):
        serializer = VideoChunkSerializer(data=request.data)
        if serializer.is_valid():
            # Save the video chunk to the 'media/chunks/' directory
            video_chunk_instance = serializer.save()

            # Convert video chunk to audio
            video_path = video_chunk_instance.video_chunk.path
            print(video_path)
            audio_path = os.path.splitext(video_path)[0] + ".wav"  # Change the audio format to WAV
            # audio_path = os.path.splitext(video_path)[0] + ".mp3"
            print(audio_path)

            video_clip = mp.VideoFileClip(video_path)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(audio_path)

            # Transcribe audio to manuscript
            recognizer = sr.Recognizer()
            print(recognizer)
            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
                # manuscript = recognizer.recognize_google(audio)
                try:
                    manuscript = recognizer.recognize_google(audio)
                    print(manuscript)
                except sr.RequestError as e:
                   return Response("Could not request results from Google Speech Recognition service; {0}".format(e))
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")


            # Update the video chunk instance with the manuscript
            video_chunk_instance.manuscript = manuscript
            video_chunk_instance.save()

            return Response(VideoChunkSerializer(video_chunk_instance).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

