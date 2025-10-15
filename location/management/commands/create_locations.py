from os.path import exists

import torch
import io
import pickle
from django.core.management.base import BaseCommand
from location.models import Location


class Command(BaseCommand):
    def handle(self, *args, **options):
        locations_EAFIT = [
            {
                "name": "Bloque 38 - Rectoría",
                "coordinates": [6.2016, -75.5785],
                "description": "Edificio administrativo principal"
            },
            {
                "name": "Biblioteca Luis Echavarría Villegas",
                "coordinates": [6.2011, -75.5784],
                "description": "Biblioteca principal de la universidad"
            },
            {
                "name": "Bloque 35",
                "coordinates": [6.2013, -75.5790],
                "description": "Edificio académico"
            },
            {
                "name": "Bloque 34",
                "coordinates": [6.2011, -75.5790],
                "description": "Edificio académico"
            },
            {
                "name": "Bloque 33",
                "coordinates": [6.2009, -75.5790],
                "description": "Edificio académico"
            },
            {
                "name": "Bloque 30",
                "coordinates": [6.2006, -75.5791],
                "description": "Edificio académico"
            },
            {
                "name": "Bloque 27",
                "coordinates": [6.2003, -75.5791],
                "description": "Edificio académico"
            },
            {
                "name": "Bloque 26 - Administración",
                "coordinates": [6.1999, -75.5792],
                "description": "Facultad de Administración"
            },
            {
                "name": "Bloque 19 - Ingeniería",
                "coordinates": [6.1986, -75.5797],
                "description": "Facultad de Ingeniería"
            },
            {
                "name": "Bloque 17",
                "coordinates": [6.1991, -75.5796],
                "description": "Edificio académico"
            },
            {
                "name": "Bloque 20",
                "coordinates": [6.1988, -75.5789],
                "description": "Edificio académico"
            },
            {
                "name": "Bloque 14",
                "coordinates": [6.1991, -75.5789],
                "description": "Edificio académico"
            },
            {
                "name": "Laboratorio del Café",
                "coordinates": [6.1999, -75.5794],
                "description": "Laboratorio del café EAFIT"
            },
            {
                "name": "Educación Continua",
                "coordinates": [6.1994, -75.5794],
                "description": "Centro de educación continua"
            },
            {
                "name": "Piscina EAFIT - Bloque 4",
                "coordinates": [6.1997, -75.5785],
                "description": "Centro deportivo - Piscina"
            },
            {
                "name": "Cancha Sintética",
                "coordinates": [6.1983, -75.5782],
                "description": "Instalaciones deportivas"
            },
            {
                "name": "Alta Dirección",
                "coordinates": [6.1980, -75.5797],
                "description": "Escuela de Alta Dirección"
            },
            {
                "name": "Departamento Desarrollo Artístico",
                "coordinates": [6.1978, -75.5792],
                "description": "Departamento de artes"
            },
            {
                "name": "Cafeteria Principal",
                "coordinates": [6.1992, -75.5785],
                "description": "Cafeteria principal"
            }
        ]

        for location in locations_EAFIT:
            exist = Location.objects.filter(name = location['name']).first()
            if not exist:
                try:
                    Location.objects.create(name = location['name'],
                                            description = location['description'],
                                            location_tensors_imgs = None,
                                            coordinates = location['coordinates'],)
                except:
                    pass
            else:
                try:
                    exist.description = location['description']
                    exist.location_tensors_imgs = None
                    exist.coordinates = location['coordinates']
                    exist.save()
                except:
                    pass
