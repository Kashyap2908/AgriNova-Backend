from django.contrib import admin
from .models import FarmerProfile,Farm
# Register your models here.
admin.site.register(Farm)
admin.site.register(FarmerProfile)