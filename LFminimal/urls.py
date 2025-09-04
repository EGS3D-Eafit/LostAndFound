from django.contrib import admin
from django.urls import path
from lugares import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.welcome, name='welcome'),   # Página inicial con 3 opciones
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('visitor/', views.visitor_login, name='visitor'),
]
