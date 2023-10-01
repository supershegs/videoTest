
from rest_framework import serializers
from .models import VideoChunk

class VideoChunkSerializer(serializers.ModelSerializer):
    manuscript = serializers.CharField(required=False)
    class Meta:
        model = VideoChunk
        fields = '__all__'