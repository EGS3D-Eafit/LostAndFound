from django.db import models
from django.conf import settings

class Location(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    coordinates = models.JSONField()
    category = models.JSONField(null=True)
    popularity = models.FloatField(null=True)
    date = models.DateField(null=True)
    connections = models.JSONField(null=True)
    location_tensors_imgs = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Relaciona un usuario con una ubicación guardada (favorita)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'location')

    def __str__(self):
        return f"{self.user.username} -> {self.location.name}"