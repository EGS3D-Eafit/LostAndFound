from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    coordinates = models.JSONField()
    location_tensors_imgs = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return self.name