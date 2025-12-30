from django.contrib import admin
from django import forms
from django.db import models
from unfold.admin import ModelAdmin, TabularInline
from .models import Cliente, Servidor

class ServidorInline(TabularInline):
    model = Servidor
    extra = 0
    fields = ('hostname', 'ip_address', 'sistema_operacional', 'descricao')
    
    formfield_overrides = {
        models.TextField: {
            'widget': forms.Textarea(
                attrs={
                    'rows': 2, 
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
    
    # AQUI: Ordenação padrão da lista por ordem alfabética
    ordering = ('nome_fantasia',)
    
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

    class Media:
        # Mantemos os scripts de melhoria visual e confirmação que criamos antes
        css = {
            'all': ('css/admin_fixes.css',)
        }
        js = ('js/admin_custom.js',)