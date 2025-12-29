from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Cliente, Servidor

class ServidorInline(TabularInline):
    model = Servidor
    extra = 0 # Mudei para 0 para não ficar criando linhas vazias sem necessidade
    
    # Definimos explicitamente os campos. 
    # Ao remover o 'show_change_link', o título duplicado sumirá.
    fields = ('hostname', 'ip_address', 'sistema_operacional', 'descricao')
    
    # IMPORTANTE: Removida a linha 'show_change_link = True' que causava a duplicação.

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