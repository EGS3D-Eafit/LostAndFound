from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


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