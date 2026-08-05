from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('weather', 'Weather'),
        ('irrigation', 'Irrigation'),
        ('market', 'Market'),
        ('disease', 'Disease Risk'),
        ('crop', 'Crop Recommendation'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    farm = models.ForeignKey('farms.Farm', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    unique_hash = models.CharField(max_length=255, unique=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} - {self.title} for {self.user.email}"
