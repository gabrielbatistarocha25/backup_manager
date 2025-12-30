from django.contrib import admin
from django import forms  # Necessário para configurar o widget
from django.db import models  # Necessário para selecionar o tipo de campo
from unfold.admin import ModelAdmin, TabularInline
from .models import Cliente, Servidor

class ServidorInline(TabularInline):
    model = Servidor
    extra = 0  # Começa sem linhas vazias extras (limpeza visual)
    fields = ('hostname', 'ip_address', 'sistema_operacional', 'descricao')
    
    # AQUI ESTÁ A MÁGICA DA CAIXA DE TEXTO PEQUENA
    formfield_overrides = {
        models.TextField: {
            'widget': forms.Textarea(
                attrs={
                    'rows': 2,  # Apenas 2 linhas de altura inicial
                    'style': 'min-height: 42px; max-height: 150px; resize: vertical;'
                }
            )
        },
    }

@admin.register(Cliente)
class ClienteAdmin(ModelAdmin):
    list_display = ('nome_fantasia', 'cnpj', 'contato_tecnico', 'ativo')
    search_fields = ('nome_fantasia', 'cnpj')
    list_filter = ('ativo',)
    
    inlines = [ServidorInline]

    fieldsets = (
        ("Dados da Empresa", {
            "fields": (("razao_social", "nome_fantasia"), "cnpj", "ativo"),
            "classes": ("tab-panel",),
        }),
        ("Contato", {
            "fields": (("contato_tecnico", "email_contato"),),
            "classes": ("tab-panel",),
        }),
    )

    # AQUI INJETAMOS O CSS QUE CRIAMOS NO PASSO 1
    class Media:
        css = {
            'all': ('css/admin_fixes.css',)
        }