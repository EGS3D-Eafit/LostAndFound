# lugares/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # lo dejamos vacío de momento
    path('api/lugares/', views.get_locations_json, name='locations_eafit'),
    path('api/compare-imgs/', views.compare_imgs, name='compare_imgs'),
]