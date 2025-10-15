import io
import torch

from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime
from PIL import Image

from location.models import Location

# Aqui va a ir lo relacionado a la conversion de imagenes

import torchvision.transforms as transforms
from transformers import AutoImageProcessor, AutoModel

import math


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
    return render(request, 'saved.html')

def filter_view(request):
    return render(request, 'filter.html')

# Datos dummy de ejemplo (puedes ajustar nombres, coords, popularidad y fecha)
DUMMY_PLACES = [
    {
        "id": 1,
        "title": "Biblioteca Luis Echavarría",
        "category": "Parque/Biblioteca",
        "description": "Libro encontrado cerca de la entrada principal.",
        "lat": 6.2014, "lng": -75.5782,
        "popularity": 12,
        "date": "2025-09-20"
    },
    {
        "id": 2,
        "title": "Cafetería Central",
        "category": "Cafetería",
        "description": "Cartera encontrada en una de las mesas.",
        "lat": 6.2009, "lng": -75.5787,
        "popularity": 30,
        "date": "2025-09-18"
    },
    {
        "id": 3,
        "title": "Bloque 19 - Ingeniería",
        "category": "Edificio",
        "description": "Chaqueta olvidada en el pasillo.",
        "lat": 6.1986, "lng": -75.5797,
        "popularity": 5,
        "date": "2025-09-22"
    },
    {
        "id": 4,
        "title": "Piscina EAFIT - Bloque 4",
        "category": "Deportes",
        "description": "Gafas encontradas cerca de la piscina.",
        "lat": 6.1997, "lng": -75.5785,
        "popularity": 8,
        "date": "2025-08-30"
    },
]

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

    # Copiar lista base
    results = DUMMY_PLACES.copy()

    # Filtrar por categoría (si se seleccionó)
    if category:
        results = [p for p in results if p['category'].lower() == category.lower()]

    # Filtrar por búsqueda de texto (título o descripción)
    if q:
        results = [p for p in results if q in p['title'].lower() or q in p['description'].lower()]

    # Si hay lat/lng y orden = nearby, calcular distancia y ordenar
    user_coords = None
    if lat and lng:
        try:
            user_lat = float(lat)
            user_lng = float(lng)
            user_coords = (user_lat, user_lng)
            for p in results:
                p['distance_km'] = haversine(user_lat, user_lng, p['lat'], p['lng'])
        except ValueError:
            user_coords = None

    # Ordenar
    if order == 'popular':
        results.sort(key=lambda x: x.get('popularity', 0), reverse=True)
    elif order == 'nearby' and user_coords:
        results.sort(key=lambda x: x.get('distance_km', 9999))
    else:  # recent por defecto
        # parse date; si falla, usa fecha mínima
        def parse_date(d):
            try:
                return datetime.fromisoformat(d)
            except Exception:
                return datetime.min
        results.sort(key=lambda x: parse_date(x.get('date','1970-01-01')), reverse=True)

    # Lista de categorías para el select (puedes mejorarla)
    categories = sorted(list({p['category'] for p in DUMMY_PLACES}))

    context = {
        'places': results,
        'categories': categories,
        'q': request.GET.get('q',''),
        'selected_category': category,
        'selected_order': order,
        'user_lat': lat or '',
        'user_lng': lng or '',
    }
    return render(request, 'filter.html', context)


from django.shortcuts import render

# Lugares de ejemplo
LUGARES = [
    {
        "id": 1,
        "nombre": "Parque de los Deseos",
        "descripcion": "Un lugar ideal para descansar.",
        "imagen": "lugares/parque.jpg"
    },
    {
        "id": 2,
        "nombre": "Café Central",
        "descripcion": "El café más famoso del centro.",
        "imagen": "lugares/cafe.jpg"
    },
    {
        "id": 3,
        "nombre": "Biblioteca EAFIT",
        "descripcion": "Espacio académico y cultural.",
        "imagen": "lugares/biblioteca.jpg"
    },
]

def saved(request):
    return render(request, "saved.html", {"lugares": LUGARES})

def saved_detail(request, lugar_id):
    lugar = next((l for l in LUGARES if l["id"] == lugar_id), None)
    return render(request, "saved_detail.html", {"lugar": lugar})

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
    for location in Location.objects.all():
        buffer = io.BytesIO(location.location_tensors_imgs)
        location_embs = torch.load(buffer)
        total = 0.0
        carry = 0.0
        for emb in location_embs:
            usr_emb = usr_image_embedding.unsqueeze(0)
            loc_emb = emb.unsqueeze(0)
            cos = torch.nn.functional.cosine_similarity(usr_emb, loc_emb).item()
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



def get_locations_json(request):
    locations = Location.objects.all()
    data = [
        {
            'nombre': location.name,
            'descripcion': location.description,
            'coords': location.coordinates,
        }
        for location in locations
    ]
    return JsonResponse(data, safe=False)
