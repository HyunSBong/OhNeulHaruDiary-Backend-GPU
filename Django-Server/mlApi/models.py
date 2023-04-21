from django.db import models

class MLItem(models.Model):
    full_diary = models.TextField(max_length=500, null=True)
    full_dialog = models.TextField(max_length=500, null=True)
    prompt = models.TextField(max_length=200, null=True)
    url = models.TextField(null=True)
    thumbnail_url = models.TextField(null=True)