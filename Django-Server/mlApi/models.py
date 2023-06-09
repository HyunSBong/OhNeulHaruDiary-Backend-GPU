from django.db import models

class MLItem(models.Model):
    full_diary = models.TextField(null=True)
    full_dialog = models.TextField(null=True)
    prompt = models.TextField(null=True)
    url = models.TextField(null=True)
    thumbnail_url = models.TextField(null=True)
