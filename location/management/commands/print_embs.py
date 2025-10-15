import io
import os
import torch
from django.core.management.base import BaseCommand
from location.models import Location

class Command(BaseCommand):
    def handle(self, *args, **options):
        for location in Location.objects.all():
            if location.location_tensors_imgs is not None:
                try:
                    buffer = io.BytesIO(location.location_tensors_imgs)
                    embeddings = torch.load(buffer)
                    print(f"{location.name}: {len(embeddings)} embeddings cargados.")
                except Exception as e:
                    print(f"Error al cargar embeddings de {location.name}: {e}")
