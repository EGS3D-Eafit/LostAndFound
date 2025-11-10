from os.path import exists

import torch
import io
import pickle
import math
from django.core.management.base import BaseCommand
from location.models import Location


class Command(BaseCommand):
    def handle(self, *args, **options):
        locations_EAFIT = [
            {
                "name": "Bloque 38 - Rectoría",
                "coordinates": [6.2016, -75.5785],
                "description": "Edificio administrativo principal",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Biblioteca Luis Echavarría Villegas",
                "coordinates": [6.2011, -75.5784],
                "description": "Biblioteca principal de la universidad",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Bloque 35",
                "coordinates": [6.2013, -75.5790],
                "description": "Edificio académico",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Bloque 34",
                "coordinates": [6.2011, -75.5790],
                "description": "Edificio académico",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Bloque 33",
                "coordinates": [6.2009, -75.5790],
                "description": "Edificio académico",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Bloque 30",
                "coordinates": [6.2006, -75.5791],
                "description": "Edificio académico",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Bloque 27",
                "coordinates": [6.2003, -75.5791],
                "description": "Edificio académico",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Bloque 26 - Administración",
                "coordinates": [6.1999, -75.5792],
                "description": "Facultad de Administración",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Bloque 19 - Ingeniería",
                "coordinates": [6.1986, -75.5797],
                "description": "Facultad de Ingeniería",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Bloque 17",
                "coordinates": [6.1991, -75.5796],
                "description": "Edificio académico",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Bloque 20",
                "coordinates": [6.1988, -75.5789],
                "description": "Edificio académico",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Bloque 14",
                "coordinates": [6.1991, -75.5789],
                "description": "Edificio académico",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Laboratorio del Café",
                "coordinates": [6.1999, -75.5794],
                "description": "Laboratorio del café EAFIT",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Educación Continua",
                "coordinates": [6.1994, -75.5794],
                "description": "Centro de educación continua",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Piscina EAFIT - Bloque 4",
                "coordinates": [6.1997, -75.5785],
                "description": "Centro deportivo - Piscina",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Cancha Sintética",
                "coordinates": [6.1983, -75.5782],
                "description": "Instalaciones deportivas",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Alta Dirección",
                "coordinates": [6.1980, -75.5797],
                "description": "Escuela de Alta Dirección",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Departamento Desarrollo Artístico",
                "coordinates": [6.1978, -75.5792],
                "description": "Departamento de artes",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            },
            {
                "name": "Cafeteria Principal",
                "coordinates": [6.1992, -75.5785],
                "description": "Cafeteria principal",
                "category": ["Parque","Biblioteca"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2011, -75.5784]]]]
            }
        ]

        for location in locations_EAFIT:
            exist = Location.objects.filter(name = location['name']).first()
            if not exist:
                try:
                    for connection in location['connections']:
                        distance = 0;
                        lastPoint = location['coordinates']
                        for point in connection[1]:
                            distance += math.sqrt(pow(lastPoint[0] - point[0], 2) + pow(lastPoint[1] - point[1], 2))
                            lastPoint = point
                        connection.insert(1, distance)

                    Location.objects.create(name = location['name'],
                                            description = location['description'],
                                            coordinates = location['coordinates'],
                                            category = location['category'],
                                            popularity = location['popularity'],
                                            date = location['date'],
                                            connections=location['connections'],
                                            location_tensors_imgs = None,)
                except Exception as e:
                    print(f"Error al procesar {location['name']}: {e}")
                except:
                    pass
            else:
                try:
                    for connection in location['connections']:
                        distance = 0;
                        lastPoint = location['coordinates']
                        for point in connection[1]:
                            distance += math.sqrt(pow(lastPoint[0] - point[0], 2) + pow(lastPoint[1] - point[1], 2))
                            lastPoint = point
                        connection.insert(1, distance)

                    exist.description = location['description']
                    #exist.location_tensors_imgs = None
                    exist.coordinates = location['coordinates']
                    exist.category = location['category']
                    exist.popularity = location['popularity']
                    exist.date = location['date']
                    exist.connections = location['connections']
                    exist.save()
                except:
                    pass
