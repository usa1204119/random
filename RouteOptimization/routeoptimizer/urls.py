from django.urls import path
from . import views

urlpatterns = [
    # Other URL patterns...
    path('', views.input_view, name='input'),  # URL for the input form view
    path('about/', views.about_view, name='about'),  # URL for the about view
    path('calculate_route/', views.calculate_route, name='calculate_route'),  # URL for the calculate_route view
]
