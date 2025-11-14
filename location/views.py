import io
import torch
import heapq
import json
import logging

from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime
from PIL import Image

from location.models import Favorite
from location.models import Location

# Aqui va a ir lo relacionado a la conversion de imagenes

import torchvision.transforms as transforms
from transformers import AutoImageProcessor, AutoModel

import math


locationsEafit = Location.objects.all()

# Página de bienvenida con opciones: Sign Up / Log In / Visitor
def welcome(request):
    return render(request, "welcome.html")


# Registro de usuario (Sign Up)
def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        # Evita duplicar usuarios
        if User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe. Intenta con otro.")
            return redirect("signup")

        # Crea el nuevo usuario
        user = User.objects.create_user(username=username, password=password)
        login(request, user)  # Lo loguea inmediatamente
        return redirect("home")

    return render(request, "signup.html")


# Iniciar sesión (Log In)
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return redirect("login")

    return render(request, "login.html")


# Cerrar sesión
def logout_view(request):
    logout(request)
    return redirect("welcome")


# Entrar como visitante
def visitor_login(request):
    request.session["visitor"] = True  # Guarda que es visitante
    return redirect("home")


# Página principal (Home)
def home(request):
    if request.user.is_authenticated:
        nombre = request.user.username  # Si tiene cuenta
    elif request.session.get("visitor"):
        nombre = "Visitante"  # Si entró como visitante
    else:
        return redirect("welcome")  # Si no está autenticado, vuelve a welcome

    return render(request, "home.html", {"nombre": nombre})

def calendar_view(request):
    return render(request, 'calendar.html')
def saved_view(request):
    # Mostrar los favoritos del usuario autenticado o los guardados en sesión
    lugares = []
    if request.user.is_authenticated:
        favs = Favorite.objects.filter(user=request.user).select_related('location')
        lugares = [f.location for f in favs]
    else:
        # favoritos en sesión: lista de location ids
        sess = request.session.get('favorites', [])
        lugares = Location.objects.filter(id__in=sess)

    return render(request, 'saved.html', {"lugares": lugares})
def filter_view(request):
    return render(request, 'filter.html')

def haversine(lat1, lon1, lat2, lon2):
    # distancia en kilómetros
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def filter_view(request):
    # Parámetros GET
    q = request.GET.get('q', '').strip().lower()
    category = request.GET.get('category', '').strip()
    order = request.GET.get('order', 'recent')  # 'recent' | 'popular' | 'nearby'
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')

    # Filtrar por categoría
    results = []
    for p in locationsEafit:
        # Si no hay categoría seleccionada, incluir todo
        # Si hay categoría, verificar si está en la lista de categorías del objeto
        if not category or category.lower() in [c.lower() for c in p.category]:
            results.append(p)

    # Filtrar por búsqueda (name o description)
    if q:
        results = [p for p in results if q in p.name.lower() or q in p.description.lower()]

    # Calcular distancia si hay coordenadas
    user_coords = None
    if lat and lng:
        try:
            user_lat = float(lat)
            user_lng = float(lng)
            user_coords = (user_lat, user_lng)
            for p in results:
                # Asignar distancia como atributo dinámico
                p.distance_km = haversine(user_lat, user_lng, p.lat, p.lng)
        except ValueError:
            user_coords = None

    # Ordenar resultados
    if order == 'popular':
        results.sort(key=lambda p: getattr(p, 'popularity', 0), reverse=True)
    elif order == 'nearby' and user_coords:
        results.sort(key=lambda p: getattr(p, 'distance_km', 9999))
    else:  # recent por defecto
        results.sort(key=lambda p: getattr(p, 'date', datetime.min), reverse=True)

    # Categorías únicas para el select
    categories = sorted({c for p in locationsEafit for c in p.category})

    # Contexto para la plantilla
    context = {
        'places': results,
        'categories': categories,
        'q': request.GET.get('q', ''),
        'selected_category': category,
        'selected_order': order,
        'user_lat': lat or '',
        'user_lng': lng or '',
    }

    return render(request, 'filter.html', context)



def saved_detail(request, lugar_id):
    try:
        lugar = Location.objects.get(id=lugar_id)
    except Location.DoesNotExist:
        lugar = None
    return render(request, "saved_detail.html", {"lugar": lugar})

def toggle_favorite(request):
    """API para agregar/quitar favoritos.
    Si el usuario está autenticado, se guarda en la tabla Favorite.
    Si es visitante, se mantiene una lista en session['favorites'] con los ids.
    Espera JSON: {"action":"add"|"remove","location_id": 12}
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        loc_id = int(data.get('location_id'))
        action = data.get('action', 'add')
    except Exception:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)

    try:
        loc = Location.objects.get(id=loc_id)
    except Location.DoesNotExist:
        return JsonResponse({'error': 'Ubicación no encontrada'}, status=404)

    if request.user.is_authenticated:
        if action == 'add':
            fav, created = Favorite.objects.get_or_create(user=request.user, location=loc)
            return JsonResponse({'status': 'added', 'location_id': loc_id})
        else:
            Favorite.objects.filter(user=request.user, location=loc).delete()
            return JsonResponse({'status': 'removed', 'location_id': loc_id})
    else:
        sess = request.session.get('favorites', [])
        if action == 'add':
            if loc_id not in sess:
                sess.append(loc_id)
                request.session['favorites'] = sess
            return JsonResponse({'status': 'added', 'location_id': loc_id})
        else:
            if loc_id in sess:
                sess.remove(loc_id)
                request.session['favorites'] = sess
            return JsonResponse({'status': 'removed', 'location_id': loc_id})

def get_favorites_api(request):
    """API que devuelve la lista de favoritos del usuario (JSON)."""
    lugares = []
    if request.user.is_authenticated:
        favs = Favorite.objects.filter(user=request.user).select_related('location')
        lugares = [
            {
                'id': f.location.id,
                'nombre': f.location.name,
                'descripcion': f.location.description,
                'coords': f.location.coordinates,
            } for f in favs
        ]
    else:
        sess = request.session.get('favorites', [])
        qs = Location.objects.filter(id__in=sess)
        lugares = [
            {'id': l.id, 'nombre': l.name, 'descripcion': l.description, 'coords': l.coordinates}
            for l in qs
        ]
    return JsonResponse(lugares, safe=False)
def createTensor(img):
    model_ckpt = "nateraw/vit-base-beans"
    processor = AutoImageProcessor.from_pretrained(model_ckpt)
    model = AutoModel.from_pretrained(model_ckpt)

    transform = transforms.Compose([
        transforms.Resize((224, 224)),  # resize to 224x224
        transforms.ToTensor(),  # convert to tensor (C x H x W, values in [0,1])
    ])

    # Apply transform
    img_tensor = transform(img).unsqueeze(0)
    embeddings = model(img_tensor).last_hidden_state[:, 0].cpu()
    return embeddings

def compare_imgs(request):
    usr_image_file = request.FILES['image']
    usr_image = Image.open(usr_image_file)
    usr_image_embedding = createTensor(usr_image)
    max_coincidence_location = None
    max_coincidence_location_mean = 0
    for location in locationsEafit:
        if(location.location_tensors_imgs is None):
            continue
        buffer = io.BytesIO(location.location_tensors_imgs)
        location_embs = torch.load(buffer)
        total = 0.0
        carry = 0.0
        for emb in location_embs:
            usr_emb = usr_image_embedding
            loc_emb = emb
            cos = torch.nn.functional.cosine_similarity(usr_emb, loc_emb, dim=1).item()
            carry += cos
            total += 1
        mean = carry / total
        if mean > max_coincidence_location_mean:
            max_coincidence_location = location
            max_coincidence_location_mean = mean

    data = [
        {
            'nombre': max_coincidence_location.name,
            'descripcion': max_coincidence_location.description,
            'coords': max_coincidence_location.coordinates,
        }
    ]

    return JsonResponse(data, safe=False)


def dijkstra(inicio_name, fin_name):
    #diccionario para sacar rapido las locaciones
    ubicaciones = {loc.name: loc for loc in locationsEafit}

    heap = [(0, inicio_name, [inicio_name], [])]
    visitados = set()

    while heap:
        distancia, actual_name, ruta, totalRoute = heapq.heappop(heap)

        if actual_name in visitados:
            continue
        visitados.add(actual_name)

        if actual_name == fin_name:
            return [{
                "ruta": ruta,
                "distancia_total": distancia,
                "ruta_total": totalRoute
            }]

        actual = ubicaciones.get(actual_name)
        if not actual:
            continue  # Si no se encuentra la ubicación, se omite

        for connection in actual.connections:
            vecino_name = connection[0]
            dist = connection[1]
            pasos = connection[2]

            if vecino_name not in visitados:
                heapq.heappush(heap, (
                    distancia + dist,
                    vecino_name,
                    ruta + [vecino_name],
                    totalRoute + pasos
                ))

    return None


def calcular_ruta(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            Location.objects.get(name=data["from"])
            Location.objects.get(name=data["to"])
        except Location.DoesNotExist:
            return JsonResponse({"error": "Ubicación no encontrada"}, status=404)

        resultado = dijkstra(data["from"], data["to"])
        if resultado:
            return JsonResponse(resultado, safe=False)
        else:
            return JsonResponse({"error": "No se encontró una ruta"}, status=404)


def get_locations_json(request):
    data = [
        {
            'id': location.id,
            'nombre': location.name,
            'descripcion': location.description,
            'coords': location.coordinates,
        }
        for location in locationsEafit
    ]
    return JsonResponse(data, safe=False)

def get_location_detail(request, nombre):
    """API para obtener los detalles completos de una ubicación con conexiones"""
    try:
        location = Location.objects.get(name=nombre)
        data = {
            'nombre': location.name,
            'descripcion': location.description,
            'coords': location.coordinates,
            'category': location.category,
            'popularity': location.popularity,
            'date': location.date,
            'connections': location.connections,
        }
        return JsonResponse(data, safe=False)
    except Location.DoesNotExist:
        return JsonResponse({'error': 'Ubicación no encontrada'}, status=404)
