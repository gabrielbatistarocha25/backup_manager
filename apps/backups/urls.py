from django.urls import path
from . import views

urlpatterns = [
    # Dashboard e Histórico
    path('', views.dashboard, name='dashboard'),
    path('historico/', views.historico_global, name='historico_global'),
    
    # Nova Tela de Relatórios
    path('relatorios/', views.painel_relatorios, name='painel_relatorios'),
    path('relatorios/excel/', views.gerar_relatorio_excel, name='gerar_excel'),
    path('relatorios/pdf/', views.gerar_relatorio_pdf, name='gerar_pdf'),

    # Validação e APIs
    path('nova-validacao/<int:cliente_id>/', views.nova_validacao, name='nova_validacao'),
    path('api/servidores-por-cliente/', views.get_servidores_por_cliente, name='get_servidores_por_cliente'),
    path('api/rotinas-cliente/<int:cliente_id>/', views.get_rotinas_cliente, name='get_rotinas_cliente'),
]