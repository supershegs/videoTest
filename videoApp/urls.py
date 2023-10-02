from django.urls import path
from .views import *

urlpatterns =[
    path('docs/', VideoChunkUploadView.as_view(), name='video-chunk-upload'),
]