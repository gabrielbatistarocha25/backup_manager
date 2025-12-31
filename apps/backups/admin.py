from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.utils.timezone import localtime
from unfold.admin import ModelAdmin
from .models import FerramentaBackup, RotinaBackup, ValidacaoBackup
from apps.clientes.models import Cliente, Servidor 

# --- CONFIGURAÇÃO PADRÃO DO UNFOLD ---
admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass

@admin.register(Group)
class GroupAdmin(ModelAdmin):
    pass

@admin.register(FerramentaBackup)
class FerramentaBackupAdmin(ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

# --- FORMULÁRIO CUSTOMIZADO (ROTINAS) ---
class RotinaBackupForm(forms.ModelForm):
    class Meta:
        model = RotinaBackup
        fields = '__all__'
        widgets = {
            # CORREÇÃO DO MODO ESCURO AQUI:
            # Adicionei classes 'dark:...' para inverter as cores quando o tema escuro estiver ativo.
            'horario_execucao': forms.TextInput(
                attrs={
                    'class': (
                        'time-picker-custom border border-gray-300 text-gray-900 text-sm rounded-lg '
                        'focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 '
                        'bg-white '  # Cor Light (Fundo Branco)
                        'dark:bg-slate-800 dark:border-slate-600 dark:text-white dark:focus:border-blue-500' # Cor Dark (Fundo Escuro)
                    ),
                    'placeholder': 'Selecione a hora...'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Ordenação alfabética dos clientes no Dropdown
        if 'cliente' in self.fields:
            self.fields['cliente'].queryset = Cliente.objects.order_by('nome_fantasia')
        
        # 2. Lógica para filtrar a lista de servidores (Ajax / Edição)
        if self.instance and self.instance.pk:
            if self.instance.cliente:
                self.fields['servidores'].queryset = Servidor.objects.filter(cliente=self.instance.cliente)
            else:
                self.fields['servidores'].queryset = Servidor.objects.none()
        elif self.data and 'cliente' in self.data:
            try:
                cliente_id = int(self.data.get('cliente'))
                self.fields['servidores'].queryset = Servidor.objects.filter(cliente_id=cliente_id)
            except (ValueError, TypeError):
                self.fields['servidores'].queryset = Servidor.objects.none()
        else:
            self.fields['servidores'].queryset = Servidor.objects.none()

@admin.register(RotinaBackup)
class RotinaBackupAdmin(ModelAdmin):
    form = RotinaBackupForm
    list_display = ('ferramenta', 'cliente', 'descricao', 'frequencia', 'get_clientes_count')
    list_filter = ('cliente', 'ferramenta', 'frequencia')
    search_fields = ('descricao', 'ferramenta__nome', 'cliente__nome_fantasia')
    fields = ('cliente', 'ferramenta', 'descricao', 'servidores', 'frequencia', 'horario_execucao', 'retencao_dias')

    class Media:
        # Carrega os scripts de comportamento (Filtro e Toast)
        js = ('js/rotina_admin.js', 'js/admin_custom.js')

    def get_clientes_count(self, obj):
        return obj.servidores.count()
    get_clientes_count.short_description = "Qtd. Servidores"

# --- ADMIN DE VALIDAÇÕES ---
@admin.register(ValidacaoBackup)
class ValidacaoBackupAdmin(ModelAdmin):
    list_display = (
        'get_status_badge', 
        'get_cliente_info', 
        'get_rotina_info', 
        'get_data_hora', 
        'get_usuario_avatar', 
        'get_edit_info'
    )
    
    list_filter = ('status', 'rotina__ferramenta', 'created_at')
    search_fields = ('rotina__descricao', 'usuario__username', 'rotina__servidores__cliente__nome_fantasia')
    readonly_fields = ('created_at', 'updated_at', 'usuario', 'editado_por')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'rotina', 'rotina__ferramenta', 'usuario', 'editado_por'
        ).prefetch_related('rotina__servidores__cliente')

    # Badge Colorido de Status (com suporte a Dark Mode já configurado)
    def get_status_badge(self, obj):
        colors = {
            'SUCESSO': 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900 dark:text-green-100 dark:border-green-700',
            'ALERTA': 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900 dark:text-yellow-100 dark:border-yellow-700',
            'ERRO': 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900 dark:text-red-100 dark:border-red-700',
        }
        css_class = colors.get(obj.status, 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200')
        icon = {'SUCESSO': 'check_circle', 'ALERTA': 'warning', 'ERRO': 'error'}.get(obj.status, 'help')
        
        return format_html(
            '<div class="flex items-center gap-2"><span class="material-symbols-outlined text-sm">{}</span><span class="px-2.5 py-0.5 rounded-full text-xs font-medium border {}">{}</span></div>',
            icon, css_class, obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'

    def get_cliente_info(self, obj):
        servidor = obj.rotina.servidores.first()
        if servidor:
            return format_html(
                '<div class="flex flex-col"><span class="font-bold text-gray-900 dark:text-gray-200">{}</span><span class="text-xs text-gray-500 dark:text-gray-400">{}</span></div>',
                servidor.cliente.nome_fantasia, servidor.hostname
            )
        return "-"
    get_cliente_info.short_description = 'Cliente / Servidor'

    def get_rotina_info(self, obj):
        return format_html(
            '<div class="flex flex-col"><span class="font-medium text-blue-600 dark:text-blue-400">{}</span><span class="text-xs text-gray-500 dark:text-gray-400">{}</span></div>',
            obj.rotina.ferramenta.nome, obj.rotina.descricao
        )
    get_rotina_info.short_description = 'Rotina'

    def get_data_hora(self, obj):
        # Data de criação
        return format_html('<div class="text-sm font-mono text-gray-600 dark:text-gray-400">{}</div>', obj.created_at.strftime('%d/%m/%Y %H:%M'))
    get_data_hora.short_description = 'Realizado em'

    def get_usuario_avatar(self, obj):
        return format_html(
            '<div class="flex items-center gap-2"><div class="w-6 h-6 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-600 dark:text-slate-200">{}</div><span class="text-sm dark:text-gray-300">{}</span></div>',
            obj.usuario.username[0].upper(), obj.usuario.username
        )
    get_usuario_avatar.short_description = 'Validador'

    # --- CAMPO AUDITORIA (Mantido com suporte a Dark Mode) ---
    def get_edit_info(self, obj):
        # Exibe se tiver editor OU se passou mais de 60s da criação
        if obj.editado_por or (obj.updated_at - obj.created_at).total_seconds() > 60:
            editor = obj.editado_por.username if obj.editado_por else "Sistema"
            
            # Converte para o fuso horário local (America/Sao_Paulo) definido no settings
            data_edit = localtime(obj.updated_at).strftime('%d/%m %H:%M')
            
            # Usei &nbsp; para forçar o espaçamento visual correto
            return format_html(
                '<span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800 border border-orange-200 dark:bg-orange-900 dark:text-orange-100 dark:border-orange-700">'
                '<span class="material-symbols-outlined text-[10px] mr-1">edit</span>'
                'Editado por&nbsp;<strong>{}</strong>&nbsp;em {}'
                '</span>',
                editor.upper(), data_edit
            )
        return "-"
    get_edit_info.short_description = 'Auditoria'

    def save_model(self, request, obj, form, change):
        if change:
            obj.editado_por = request.user
        super().save_model(request, obj, form, change)