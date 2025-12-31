from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.utils.timezone import localtime
from unfold.admin import ModelAdmin
from .models import FerramentaBackup, RotinaBackup, ValidacaoBackup
from apps.clientes.models import Cliente, Servidor 

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
            'horario_execucao': forms.TextInput(attrs={'type': 'time', 'class': 'vTimeField'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'cliente' in self.fields:
            self.fields['cliente'].queryset = Cliente.objects.order_by('nome_fantasia')
        
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
    
    # ADICIONEI 'conteudo' NA LISTAGEM
    list_display = ('ferramenta', 'cliente', 'descricao', 'conteudo', 'frequencia', 'get_clientes_count')
    list_filter = ('cliente', 'ferramenta', 'frequencia')
    
    # ADICIONEI 'conteudo' NA BUSCA
    search_fields = ('descricao', 'conteudo', 'ferramenta__nome', 'cliente__nome_fantasia')
    
    # ADICIONEI 'conteudo' NO FORMULÁRIO DE EDIÇÃO
    fields = ('cliente', 'ferramenta', 'descricao', 'conteudo', 'servidores', 'frequencia', 'horario_execucao', 'retencao_dias')

    class Media:
        js = ('js/rotina_admin.js',)

    def get_clientes_count(self, obj):
        return obj.servidores.count()
    get_clientes_count.short_description = "Qtd. Servidores"


@admin.register(ValidacaoBackup)
class ValidacaoBackupAdmin(ModelAdmin):
    list_display = ('get_status_badge', 'get_cliente_info', 'get_rotina_info', 'get_data_hora', 'get_usuario_avatar', 'get_edit_info')
    list_filter = ('status', 'rotina__ferramenta', 'created_at')
    search_fields = ('rotina__descricao', 'usuario__username', 'rotina__servidores__cliente__nome_fantasia')
    readonly_fields = ('created_at', 'updated_at', 'usuario', 'editado_por')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('rotina', 'rotina__ferramenta', 'usuario', 'editado_por').prefetch_related('rotina__servidores__cliente')

    def get_status_badge(self, obj):
        colors = {
            'SUCESSO': 'bg-green-100 text-green-800 border-green-200',
            'ALERTA': 'bg-yellow-100 text-yellow-800 border-yellow-200',
            'ERRO': 'bg-red-100 text-red-800 border-red-200'
        }
        css_class = colors.get(obj.status, 'bg-gray-100 text-gray-800')
        icon = {'SUCESSO': 'check_circle', 'ALERTA': 'warning', 'ERRO': 'error'}.get(obj.status, 'help')
        return format_html('<div class="flex items-center gap-2"><span class="material-symbols-outlined text-sm">{}</span><span class="px-2.5 py-0.5 rounded-full text-xs font-medium border {}">{}</span></div>', icon, css_class, obj.get_status_display())
    get_status_badge.short_description = 'Status'

    def get_cliente_info(self, obj):
        servidor = obj.rotina.servidores.first()
        return format_html('<div class="flex flex-col"><span class="font-bold text-gray-900">{}</span><span class="text-xs text-gray-500">{}</span></div>', servidor.cliente.nome_fantasia, servidor.hostname) if servidor else "-"
    get_cliente_info.short_description = 'Cliente / Servidor'

    def get_rotina_info(self, obj):
        return format_html('<div class="flex flex-col"><span class="font-medium text-blue-600">{}</span><span class="text-xs text-gray-500">{}</span></div>', obj.rotina.ferramenta.nome, obj.rotina.descricao)
    get_rotina_info.short_description = 'Rotina'

    def get_data_hora(self, obj):
        return format_html('<div class="text-sm font-mono text-gray-600">{}</div>', obj.created_at.strftime('%d/%m/%Y %H:%M'))
    get_data_hora.short_description = 'Realizado em'

    def get_usuario_avatar(self, obj):
        return format_html('<div class="flex items-center gap-2"><div class="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600">{}</div><span class="text-sm">{}</span></div>', obj.usuario.username[0].upper(), obj.usuario.username)
    get_usuario_avatar.short_description = 'Validador'

    def get_edit_info(self, obj):
        if obj.editado_por or (obj.updated_at - obj.created_at).total_seconds() > 60:
            editor = obj.editado_por.username if obj.editado_por else "Sistema"
            data_edit = localtime(obj.updated_at).strftime('%d/%m %H:%M')
            return format_html('<span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800 border border-orange-200"><span class="material-symbols-outlined text-[10px] mr-1">edit</span>Editado por&nbsp;<strong>{}</strong>&nbsp;em {}</span>', editor.upper(), data_edit)
        return "-"
    get_edit_info.short_description = 'Auditoria'

    def save_model(self, request, obj, form, change):
        if change:
            obj.editado_por = request.user
        super().save_model(request, obj, form, change)