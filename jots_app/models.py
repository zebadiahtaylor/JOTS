from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    is_leader = models.BooleanField(default=False)
    main_collection = models.ForeignKey('Collection', verbose_name='Collection', 
                            on_delete=models.CASCADE, null=True, blank=True)
    is_subscriber = models.BooleanField(default=False)
    collection_invites = models.ManyToManyField('Collection', related_name='collection_invites', blank=True)
    dark_mode = models.BooleanField(default=False)

class Collection(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=200, blank=True)
    leader = models.ForeignKey(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    scheduled_sessions = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.leader}'s {self.title}."


class Note(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    tag = models.ForeignKey('Tag', verbose_name='Tag', on_delete=models.SET_DEFAULT, blank=True, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_by')
    archived = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.text}'


class Tag(models.Model):
    name = models.CharField(max_length=100)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'


class Article(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    tag = models.ForeignKey('Tag', verbose_name='Tag', on_delete=models.SET_DEFAULT, blank=True, default=None, null=True)
    content_slug = models.SlugField(max_length=1000, blank=True, default="error")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_updated_by')
    views = models.PositiveIntegerField(default=0)