from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


class Entry(models.Model):
    DIARY, TWEET = 'DIARY', 'TWEET'
    SOURCE_TYPES = (
        (DIARY, DIARY),
        (TWEET, TWEET),
    )
    content = models.TextField(blank=True)
    raw = models.TextField(blank=True)
    preprocessed_content = models.TextField(blank=True)
    author = models.CharField(max_length=20, blank=True)
    media = models.CharField(max_length=200, blank=True)
    source_type = models.CharField(max_length=10, choices=SOURCE_TYPES, blank=True)
    source_id = models.CharField(max_length=20, blank=True)
    golden = models.BooleanField(default=False)

    def __str__(self):
        return '{} - {}:{:50s}'.format(self.source_type, self.author, self.content)


class Annotation(models.Model):
    UNDONE, PENDING, DONE = 'UNDONE', 'PENDING', 'DONE'
    STATUS_CHOICES = (
        (UNDONE, UNDONE),
        (PENDING, PENDING),
        (DONE, DONE)
    )
    entry = models.ForeignKey(Entry)
    user = models.ForeignKey(User)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=UNDONE)
    update_time = models.DateTimeField(default=datetime.now)
    annotation = models.TextField(blank=True)
    raw = models.TextField(blank=True)
