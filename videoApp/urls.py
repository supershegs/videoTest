from django.urls import path
from .views import *

urlpatterns =[
    path('upload/', VideoChunkUploadView.as_view(), name='video-chunk-upload'),
]