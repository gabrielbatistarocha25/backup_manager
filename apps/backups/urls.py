from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('historico/', views.historico_global, name='historico_global'),
    path('validar/<int:cliente_id>/', views.nova_validacao, name='nova_validacao'),
    
    # NOVA ROTA PARA O AJAX DO ADMIN
    path('api/servidores-por-cliente/', views.get_servidores_por_cliente, name='ajax_servidores_cliente'),
]