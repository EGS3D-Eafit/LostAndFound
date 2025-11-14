from django.core.management.base import BaseCommand
from location.models import Location


class Command(BaseCommand):
    def handle(self, *args, **options):
        deletelocations = [
            "Laboratorio del Café"
        ]
        for to_delete in deletelocations:
            location = Location.objects.filter(name=to_delete).first()
            try:
                if location:
                    location.delete()
            except Exception as e:
                print(f"✗ No se pudo eliminar el objeto {to_delete} por favor asegurese de que su escritura sea correcta")
                continue
        print("\n=== Proceso completado ===\n")