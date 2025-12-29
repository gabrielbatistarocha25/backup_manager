from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('validar/<int:cliente_id>/', views.nova_validacao, name='nova_validacao'),
]