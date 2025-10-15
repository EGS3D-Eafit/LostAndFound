import io
import os
import torch
import unicodedata

from django.core.management.base import BaseCommand
from location.models import Location
from location.views import createTensor
from PIL import Image
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        for location in Location.objects.all():

            location_name = self.no_tildes(str(location.name))
            folder_path = os.path.join(settings.BASE_DIR, 'location', 'static', 'locations_img', location_name)

            if not os.path.isdir(folder_path):
                self.stdout.write(self.style.ERROR(f'La carpeta "{folder_path}" no existe'))
                continue

            extensiones_validas = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
            imgs = [f for f in os.listdir(folder_path) if f.lower().endswith(extensiones_validas)]

            embeddings = []
            for name in imgs:
                img_path = os.path.join(folder_path, name)
                try:
                    with Image.open(img_path) as img:
                        embeddings.append(createTensor(img))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Error al procesar {name}: {e}'))
                    continue

            if embeddings:
                buffer = io.BytesIO()
                torch.save(embeddings, buffer)
                embedding_bytes = buffer.getvalue()
                location.location_tensors_imgs = embedding_bytes
                location.save()

    def no_tildes(self, text):
        return ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
