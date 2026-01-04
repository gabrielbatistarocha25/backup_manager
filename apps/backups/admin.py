from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
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
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
            'description': 'Primeiro, insira um nome de usuário e uma senha. Depois, você poderá editar mais opções e permissões do usuário.',
        }),
    )

    class Media:
        css = {
            'all': ('css/admin_password_fix.css',)
        }

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
    list_display = ('ferramenta', 'cliente', 'descricao', 'conteudo', 'frequencia', 'get_clientes_count')
    list_filter = ('cliente', 'ferramenta', 'frequencia')
    search_fields = ('descricao', 'conteudo', 'ferramenta__nome', 'cliente__nome_fantasia')
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

    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',)
        }

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('rotina', 'rotina__ferramenta', 'usuario', 'editado_por').prefetch_related('rotina__servidores__cliente')

    def get_status_badge(self, obj):
        custom_css = """
        <style>
            .dark .badge-custom-sucesso { background-color: #1b3636 !important; color: #3aa868 !important; border-color: #166534 !important; font-weight: 700 !important; }
            .dark .badge-custom-alerta { background-color: #37302e !important; color: #cfa91a !important; border-color: #854d0e !important; font-weight: 700 !important; }
            .dark .badge-custom-erro { background-color: #3b2531 !important; color: #f87171 !important; border-color: #991b1b !important; font-weight: 700 !important; }
        </style>
        """

        status_config = {
            'SUCESSO': {
                'label': 'Sucesso',
                'icon': 'fa-solid fa-check',
                'classes': 'bg-green-100 text-green-800 border-green-200 badge-custom-sucesso'
            },
            'ALERTA': {
                'label': 'Alerta',
                'icon': 'fa-solid fa-triangle-exclamation',
                'classes': 'bg-yellow-100 text-yellow-800 border-yellow-200 badge-custom-alerta'
            },
            'ERRO': {
                'label': 'Erro',
                'icon': 'fa-solid fa-xmark',
                'classes': 'bg-red-100 text-red-800 border-red-200 badge-custom-erro'
            }
        }
        
        config = status_config.get(obj.status, {
            'label': obj.status,
            'icon': 'fa-solid fa-minus',
            'classes': 'bg-gray-100 text-gray-800 border-gray-200'
        })

        base_classes = "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border "
        
        return format_html(
            '{}<span class="{}{}"> <i class="{} text-[10px]"></i> {}</span>',
            mark_safe(custom_css),
            base_classes,
            config['classes'],
            config['icon'],
            config['label']
        )
    get_status_badge.short_description = 'Status'

    def get_cliente_info(self, obj):
        servidor = obj.rotina.servidores.first()
        return format_html(
            '<div class="flex flex-col"><span class="font-bold text-gray-900 dark:text-gray-100">{}</span><span class="text-xs text-gray-500 dark:text-gray-400">{}</span></div>', 
            servidor.cliente.nome_fantasia, servidor.hostname
        ) if servidor else "-"
    get_cliente_info.short_description = 'Cliente / Servidor'

    def get_rotina_info(self, obj):
        return format_html(
            '<div class="flex flex-col"><span class="font-medium text-blue-600 dark:text-blue-400">{}</span><span class="text-xs text-gray-500 dark:text-gray-400">{}</span></div>', 
            obj.rotina.ferramenta.nome, obj.rotina.descricao
        )
    get_rotina_info.short_description = 'Rotina'

    def get_data_hora(self, obj):
        return format_html(
            '<div class="text-sm font-mono text-gray-600 dark:text-gray-400">{}</div>', 
            obj.created_at.strftime('%d/%m/%Y %H:%M')
        )
    get_data_hora.short_description = 'Realizado em'

    def get_usuario_avatar(self, obj):
        return format_html(
            '<div class="flex items-center gap-2"><div class="w-6 h-6 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-600 dark:text-slate-300">{}</div><span class="text-sm dark:text-gray-200">{}</span></div>', 
            obj.usuario.username[0].upper(), obj.usuario.username
        )
    get_usuario_avatar.short_description = 'Validador'

    def get_edit_info(self, obj):
        if obj.editado_por or (obj.updated_at - obj.created_at).total_seconds() > 60:
            editor = obj.editado_por.username if obj.editado_por else "Sistema"
            data_edit = localtime(obj.updated_at).strftime('%d/%m %H:%M')
            return format_html(
                '<span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800 border border-orange-200 dark:bg-orange-900/30 dark:text-orange-400 dark:border-orange-800"><span class="material-symbols-outlined text-[10px] mr-1">edit</span>Editado por&nbsp;<strong>{}</strong>&nbsp;em {}</span>', 
                editor.upper(), data_edit
            )
        return "-"
    get_edit_info.short_description = 'Auditoria'

    def save_model(self, request, obj, form, change):
        if change:
            obj.editado_por = request.user
        super().save_model(request, obj, form, change)