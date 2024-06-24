# Import necessary modules
from django.db import models
from django.contrib.auth.models import AbstractUser
from django_cryptography.fields import encrypt

# Custom User model that extends Django's AbstractUser
class CustomUser(AbstractUser):
    # Additional fields for the user profile
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    contact_phone = models.CharField(max_length=15, blank=True)
    # Many-to-many relationship with Event model (for saved events)
    saved_events = models.ManyToManyField('Event', blank=True, related_name='saved_by_users')

    def __str__(self):
        # String representation of the user (username)
        return self.username

# Event model to store information about events
class Event(models.Model):
    name = models.CharField(max_length=100)
    # Encrypted description field for added security
    description = encrypt(models.TextField())
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=100)
    entrance = models.BooleanField(default=False)
    # Foreign key relationship with CustomUser (event organizer)
    organizer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='organized_events')
    address = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    # Choices for event status
    STATUS_CHOICES = (
        ('PL', 'Planning'),
        ('OG', 'Ongoing'),
        ('CP', 'Completed'),
        ('CN', 'Cancelled'),
    )
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='PL')
    # Choices for event category
    CATEGORY_CHOICES = [
        ('MUSIC', 'Music'),
        ('SPORTS', 'Sports'),
        ('ARTS', 'Arts & Culture'),
        ('FOOD', 'Food & Drink'),
        ('OTHER', 'Other'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')

    def __str__(self):
        # String representation of the event (event name)
        return self.name

# Message model for user-to-user messaging
class Message(models.Model):
    # Foreign key relationships with CustomUser for sender and receiver
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=100)
    # Encrypted body field for added security
    body = encrypt(models.TextField())
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def __str__(self):
        # String representation of the message
        return f'From {self.sender.username} to {self.receiver.username} - {self.subject}'