from django.contrib import admin
from django.urls import path
from location import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.welcome, name='welcome'),   # Página inicial con 3 opciones
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('visitor/', views.visitor_login, name='visitor'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('saved/', views.saved_view, name='saved'),
    path('filter/', views.filter_view, name='filter'),
    path("saved/<int:lugar_id>/", views.saved_detail, name="saved_detail"),

]