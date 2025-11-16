from django.db import models
from django.utils.text import slugify


class Destination(models.Model):
    DESTINATION_TYPES = [
        ('safari', 'Safari'),
        ('beach', 'Beach'),
        ('city', 'City'),
        ('mountain', 'Mountain'),
        ('cultural', 'Cultural'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    destination_type = models.CharField(max_length=20, choices=DESTINATION_TYPES)
    
    # Location
    county = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Details
    best_time_to_visit = models.CharField(max_length=200)
    average_cost_per_day = models.IntegerField(help_text="Average cost in KSh")
    popular_activities = models.TextField(help_text="Comma-separated activities")
    
    # Media
    image = models.ImageField(upload_to='destinations/', blank=True, null=True)
    image_url = models.URLField(blank=True, help_text="External image URL if not uploading")
    
    # Meta
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_activities_list(self):
        return [activity.strip() for activity in self.popular_activities.split(',')]
