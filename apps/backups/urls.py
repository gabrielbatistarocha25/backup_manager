from django.urls import path
from . import views

urlpatterns = [
    # Dashboard principal (Visão NOC)
    path('', views.dashboard, name='dashboard'),
    
    # Nova tela de histórico completo
    path('historico/', views.historico_global, name='historico_global'),
    
    # Formulário de validação
    path('validar/<int:cliente_id>/', views.nova_validacao, name='nova_validacao'),
]