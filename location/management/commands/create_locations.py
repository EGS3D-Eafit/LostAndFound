from os.path import exists

import torch
import io
import pickle
import math
from django.core.management.base import BaseCommand
from location.models import Location


class Command(BaseCommand):
    def calculate_distance(self, coord1, coord2):
        """Calcula la distancia entre dos coordenadas"""
        return math.sqrt(pow(coord1[0] - coord2[0], 2) + pow(coord1[1] - coord2[1], 2))
    
    def calculate_path_distance(self, path):
        """Calcula la distancia total de una ruta"""
        if len(path) < 2:
            return 0
        distance = 0
        for i in range(len(path) - 1):
            distance += self.calculate_distance(path[i], path[i + 1])
        return distance

    def handle(self, *args, **options):
        # Coordenadas más realistas para los bloques de EAFIT (Campus de Medellín)
        locations_EAFIT = [
            {
                "name": "Bloque 38 - Rectoría",
                "coordinates": [6.20165, -75.57845],
                "description": "Edificio administrativo principal",
                "category": ["Administración"],
                "popularity": 15,
                "date": "2025-09-20",
                "connections": [
                    ["Biblioteca Luis Echavarría Villegas", [[6.2016, -75.5785], [6.2014, -75.5784], [6.2011, -75.5784]]],
                    ["Bloque 35", [[6.2016, -75.5785], [6.2015, -75.5787], [6.2013, -75.5790]]]
                ]
            },
            {
                "name": "Biblioteca Luis Echavarría Villegas",
                "coordinates": [6.2011, -75.5785],
                "description": "Biblioteca principal de la universidad",
                "category": ["Biblioteca"],
                "popularity": 18,
                "date": "2025-09-20",
                "connections": [
                    ["Bloque 38 - Rectoría", [[6.2011, -75.5784], [6.2014, -75.5784], [6.2016, -75.5785]]],
                    ["Bloque 35", [[6.2011, -75.5784], [6.2012, -75.5787], [6.2013, -75.5790]]],
                    ["Cafeteria Principal", [[6.2011, -75.5784], [6.2011, -75.5784], [6.1992, -75.5785]]]
                ]
            },
            {
                "name": "Bloque 35",
                "coordinates": [6.2013, -75.5790],
                "description": "Edificio académico",
                "category": ["Académico"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [
                    ["Bloque 38 - Rectoría", [[6.2013, -75.5790], [6.2015, -75.5787], [6.2016, -75.5785]]],
                    ["Biblioteca Luis Echavarría Villegas", [[6.2013, -75.5790], [6.2012, -75.5787], [6.2011, -75.5784]]],
                    ["Bloque 34", [[6.2013, -75.5790], [6.2012, -75.5792], [6.2011, -75.5795]]]
                ]
            },
            {
                "name": "Bloque 34",
                "coordinates": [6.2011, -75.5790],
                "description": "Edificio académico",
                "category": ["Académico"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [
                    ["Bloque 35", [[6.2011, -75.5795], [6.2012, -75.5792], [6.2013, -75.5790]]],
                    ["Bloque 33", [[6.2011, -75.5795], [6.2010, -75.5797], [6.2009, -75.5800]]]
                ]
            },
            {
                "name": "Bloque 33",
                "coordinates": [6.2009, -75.5790],
                "description": "Edificio académico",
                "category": ["Académico"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [
                    ["Bloque 34", [[6.2009, -75.5800], [6.2010, -75.5797], [6.2011, -75.5795]]],
                    ["Bloque 30", [[6.2009, -75.5800], [6.2008, -75.5802], [6.2006, -75.5805]]]
                ]
            },
            {
                "name": "Bloque 30",
                "coordinates": [6.2006, -75.5791],
                "description": "Edificio académico",
                "category": ["Académico"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [
                    ["Bloque 33", [[6.2006, -75.5805], [6.2008, -75.5802], [6.2009, -75.5800]]],
                    ["Bloque 27", [[6.2006, -75.5805], [6.2005, -75.5807], [6.2003, -75.5810]]]
                ]
            },
            {
                "name": "Bloque 27",
                "coordinates": [6.2003, -75.57915],
                "description": "Edificio académico",
                "category": ["Académico"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [
                    ["Bloque 30", [[6.2003, -75.5810], [6.2005, -75.5807], [6.2006, -75.5805]]],
                    ["Bloque 26 - Administración", [[6.2003, -75.5810], [6.2001, -75.5812], [6.1999, -75.5815]]]
                ]
            },
            {
                "name": "Bloque 26 - Administración",
                "coordinates": [6.1999, -75.5815],
                "description": "Facultad de Administración",
                "category": ["Administración"],
                "popularity": 14,
                "date": "2025-09-20",
                "connections": [
                    ["Bloque 27", [[6.1999, -75.5815], [6.2001, -75.5812], [6.2003, -75.5810]]],
                    ["Laboratorio del Café", [[6.1999, -75.5815], [6.1999, -75.5804], [6.1999, -75.5794]]]
                ]
            },
            {
                "name": "Bloque 20",
                "coordinates": [6.19854, -75.5792],
                "description": "Edificio académico",
                "category": ["Académico"],
                "popularity": 13,
                "date": "2025-09-20",
                "connections": [
                    ["Bloque 19 - Ingeniería", [[6.1988, -75.5789], [6.1987, -75.5793], [6.1986, -75.5797]]],
                    ["Bloque 14", [[6.1988, -75.5789], [6.1989, -75.5787], [6.1991, -75.5785]]],
                    ["Bloque 15", [[6.1988, -75.5789], [6.1990, -75.5788], [6.1993, -75.5788]]],
                    ["Bloque 16", [[6.1988, -75.5789], [6.1988, -75.5791], [6.1989, -75.5793]]],
                    ["Piscina EAFIT - Bloque 4", [[6.1988, -75.5789], [6.1990, -75.5786], [6.1993, -75.5783], [6.1997, -75.5780]]]
                ]
            },
            {
                "name": "Bloque 19 - Ingeniería",
                "coordinates": [6.1979, -75.57965],
                "description": "Facultad de Ingeniería",
                "category": ["Académico"],
                "popularity": 16,
                "date": "2025-09-20",
                "connections": [
                    ["Bloque 20", [[6.1986, -75.5797], [6.1987, -75.5793], [6.1988, -75.5789]]],
                    ["Bloque 16", [[6.1986, -75.5797], [6.1987, -75.5795], [6.1989, -75.5793]]],
                    ["Alta Dirección", [[6.1986, -75.5797], [6.1983, -75.5797], [6.1980, -75.5797]]],
                    ["Piscina EAFIT - Bloque 4", [[6.1986, -75.5797], [6.1990, -75.5792], [6.1994, -75.5786], [6.1997, -75.5780]]]
                ]
            },
            {
                "name": "Bloque 17",
                "coordinates": [6.1991, -75.5789],
                "description": "Edificio académico",
                "category": ["Académico"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [
                    ["Bloque 20", [[6.1991, -75.5792], [6.1989, -75.5790], [6.1988, -75.5789]]],
                    ["Bloque 14", [[6.1991, -75.5792], [6.1991, -75.5788], [6.1991, -75.5785]]]
                ]
            },
            {
                "name": "Bloque 14",
                "coordinates": [6.1985, -75.5789],
                "description": "Edificio académico",
                "category": ["Académico"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [
                    ["Bloque 20", [[6.1991, -75.5785], [6.1989, -75.5787], [6.1988, -75.5789]]],
                    ["Bloque 17", [[6.1991, -75.5785], [6.1991, -75.5788], [6.1991, -75.5792]]],
                    ["Cafeteria Principal", [[6.1991, -75.5785], [6.1992, -75.5785], [6.1992, -75.5785]]],
                    ["Piscina EAFIT - Bloque 4", [[6.1991, -75.5785], [6.1994, -75.5783], [6.1997, -75.5780]]]
                ]
            },
            {
                "name": "Bloque 15",
                "coordinates": [6.1987, -75.5789],
                "description": "Edificio académico",
                "category": ["Académico"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [
                    ["Bloque 20", [[6.1993, -75.5788], [6.1990, -75.5788], [6.1988, -75.5789]]],
                    ["Bloque 16", [[6.1993, -75.5788], [6.1991, -75.5790], [6.1989, -75.5793]]]
                ]
            },
            {
                "name": "Bloque 16",
                "coordinates": [6.1989, -75.5789],
                "description": "Edificio académico",
                "category": ["Académico"],
                "popularity": 12,
                "date": "2025-09-20",
                "connections": [
                    ["Bloque 20", [[6.1989, -75.5793], [6.1988, -75.5791], [6.1988, -75.5789]]],
                    ["Bloque 15", [[6.1989, -75.5793], [6.1991, -75.5790], [6.1993, -75.5788]]],
                    ["Bloque 19 - Ingeniería", [[6.1989, -75.5793], [6.1987, -75.5795], [6.1986, -75.5797]]],
                    ["Piscina EAFIT - Bloque 4", [[6.1989, -75.5793], [6.1992, -75.5787], [6.1995, -75.5783], [6.1997, -75.5780]]]
                ]
            },
            #{
            #    "name": "Laboratorio del Café",
            #    "coordinates": [6.1999, -75.5794],
            #    "description": "Laboratorio del café EAFIT",
            #    "category": ["Laboratorio"],
            #    "popularity": 10,
            #    "date": "2025-09-20",
            #    "connections": [
            #        ["Bloque 26 - Administración", [[6.1999, -75.5794], [6.1999, -75.5804], [6.1999, -75.5815]]],
            #        ["Educación Continua", [[6.1999, -75.5794], [6.1996, -75.5797], [6.1994, -75.5800]]]
            #    ]
            #},
            {
                "name": "Educación Continua",
                "coordinates": [6.1994, -75.5800],
                "description": "Centro de educación continua",
                "category": ["Académico"],
                "popularity": 9,
                "date": "2025-09-20",
                "connections": [
                    ["Laboratorio del Café", [[6.1994, -75.5800], [6.1996, -75.5797], [6.1999, -75.5794]]],
                    ["Departamento Desarrollo Artístico", [[6.1994, -75.5800], [6.1986, -75.5802], [6.1978, -75.5805]]],
                    ["Piscina EAFIT - Bloque 4", [[6.1994, -75.5800], [6.1994, -75.5790], [6.1996, -75.5785], [6.1997, -75.5780]]]
                ]
            },
            {
                "name": "Piscina EAFIT - Bloque 4",
                "coordinates": [6.1997, -75.5780],
                "description": "Centro deportivo - Piscina",
                "category": ["Deporte"],
                "popularity": 14,
                "date": "2025-09-20",
                "connections": [
                    ["Bloque 14", [[6.1997, -75.5780], [6.1994, -75.5783], [6.1991, -75.5785]]],
                    ["Bloque 20", [[6.1997, -75.5780], [6.1993, -75.5783], [6.1990, -75.5786], [6.1988, -75.5789]]],
                    ["Bloque 19 - Ingeniería", [[6.1997, -75.5780], [6.1994, -75.5786], [6.1990, -75.5792], [6.1986, -75.5797]]],
                    ["Bloque 16", [[6.1997, -75.5780], [6.1995, -75.5783], [6.1992, -75.5787], [6.1989, -75.5793]]],
                    ["Educación Continua", [[6.1997, -75.5780], [6.1996, -75.5785], [6.1994, -75.5790], [6.1994, -75.5800]]],
                    ["Cancha Sintética", [[6.1997, -75.5780], [6.1990, -75.5781], [6.1983, -75.5782]]]
                ]
            },
            {
                "name": "Cancha Sintética",
                "coordinates": [6.1983, -75.5782],
                "description": "Instalaciones deportivas",
                "category": ["Deporte"],
                "popularity": 13,
                "date": "2025-09-20",
                "connections": [
                    ["Piscina EAFIT - Bloque 4", [[6.1983, -75.5782], [6.1990, -75.5781], [6.1997, -75.5780]]],
                    ["Alta Dirección", [[6.1983, -75.5782], [6.1981, -75.5790], [6.1980, -75.5797]]]
                ]
            },
            {
                "name": "Alta Dirección",
                "coordinates": [6.1980, -75.5797],
                "description": "Escuela de Alta Dirección",
                "category": ["Académico"],
                "popularity": 11,
                "date": "2025-09-20",
                "connections": [
                    ["Bloque 19 - Ingeniería", [[6.1980, -75.5797], [6.1983, -75.5797], [6.1986, -75.5797]]],
                    ["Cancha Sintética", [[6.1980, -75.5797], [6.1981, -75.5790], [6.1983, -75.5782]]],
                    ["Departamento Desarrollo Artístico", [[6.1980, -75.5797], [6.1979, -75.5801], [6.1978, -75.5805]]]
                ]
            },
            {
                "name": "Departamento Desarrollo Artístico",
                "coordinates": [6.1978, -75.5805],
                "description": "Departamento de artes",
                "category": ["Académico"],
                "popularity": 10,
                "date": "2025-09-20",
                "connections": [
                    ["Educación Continua", [[6.1978, -75.5805], [6.1986, -75.5802], [6.1994, -75.5800]]],
                    ["Alta Dirección", [[6.1978, -75.5805], [6.1979, -75.5801], [6.1980, -75.5797]]]
                ]
            },
            {
                "name": "Cafeteria Principal",
                "coordinates": [6.1992, -75.5785],
                "description": "Cafeteria principal",
                "category": ["Servicios"],
                "popularity": 17,
                "date": "2025-09-20",
                "connections": [
                    ["Biblioteca Luis Echavarría Villegas", [[6.1992, -75.5785], [6.2011, -75.5784], [6.2011, -75.5784]]],
                    ["Bloque 14", [[6.1992, -75.5785], [6.1991, -75.5785], [6.1991, -75.5785]]],
                    ["Piscina EAFIT - Bloque 4", [[6.1992, -75.5785], [6.1994, -75.5783], [6.1997, -75.5780]]]
                ]
            }
        ]

        # Crear o actualizar ubicaciones con cálculo de distancias
        print("\n=== Creando/Actualizando ubicaciones ===\n")
        for location in locations_EAFIT:
            exist = Location.objects.filter(name=location['name']).first()
            
            # Procesar conexiones: insertar distancia calculada en posición 1
            processed_connections = []
            for connection in location['connections']:
                nombre_destino = connection[0]
                ruta = connection[1]
                distancia = self.calculate_path_distance(ruta)
                processed_connections.append([nombre_destino, distancia, ruta])
            
            if not exist:
                try:
                    Location.objects.create(
                        name=location['name'],
                        description=location['description'],
                        coordinates=location['coordinates'],
                        category=location['category'],
                        popularity=location['popularity'],
                        date=location['date'],
                        connections=processed_connections,
                        #location_tensors_imgs=None,
                    )
                    print(f"✓ Creada: {location['name']}")
                    if processed_connections:
                        for conn in processed_connections:
                            print(f"  └─ Conecta con: {conn[0]} ({conn[1]:.6f} unidades)")
                except Exception as e:
                    print(f"✗ Error al crear {location['name']}: {e}")
            else:
                try:
                    exist.description = location['description']
                    exist.coordinates = location['coordinates']
                    exist.category = location['category']
                    exist.popularity = location['popularity']
                    exist.date = location['date']
                    exist.connections = processed_connections
                    exist.save()
                    print(f"✓ Actualizada: {location['name']}")
                    if processed_connections:
                        for conn in processed_connections:
                            print(f"  └─ Conecta con: {conn[0]} ({conn[1]:.6f} unidades)")
                except Exception as e:
                    print(f"✗ Error al actualizar {location['name']}: {e}")
        
        print("\n=== Proceso completado ===\n")
