from django.db import models

# Create your models here.
class VideoChunk(models.Model):
    video_chunk = models.FileField(upload_to='chunks/')
    manuscript = models.TextField()
    
    def __str__(self):
        return f"VideoChunk-{self.id}"