from django.db import models
from django.contrib.auth.models import User

class FarmerProfile(models.Model):
    """
    Stores farmer personal details and profile onboarding status.
    One-to-one relationship with Django's built-in User model.
    """
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    preferred_language = models.CharField(max_length=50, default='English')
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    profile_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"


class Farm(models.Model):
    """
    Stores physical farm specifications, geographic locations, and soil/irrigation properties.
    Foreign key relationship with User (a farmer can own multiple farms).
    """
    user = models.ForeignKey(User, related_name='farms', on_delete=models.CASCADE)
    farm_name = models.CharField(max_length=255)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    taluka = models.CharField(max_length=100)
    village = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    farm_area = models.DecimalField(max_digits=10, decimal_places=2)
    area_unit = models.CharField(max_length=20, default='Acres')
    soil_type = models.CharField(max_length=100)
    irrigation_type = models.CharField(max_length=100)
    water_availability = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.farm_name} - {self.village}, {self.district} ({'Active' if self.is_active else 'Inactive'})"
