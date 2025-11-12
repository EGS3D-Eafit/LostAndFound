# lugares/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # lo dejamos vacío de momento
    path('api/lugares/', views.get_locations_json, name='locations_eafit'),
    path('api/lugar/<str:nombre>/', views.get_location_detail, name='location_detail'),
    path('api/compare-imgs/', views.compare_imgs, name='compare_imgs'),
    path('api/calcular-ruta/', views.calcular_ruta, name='calcular_ruta'),
]