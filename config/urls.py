from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# --- CONFIGURAÇÕES NATIVAS DO ADMIN ---
# Definimos o Header (Título da aba)
admin.site.site_header = "MaiLou Cloud"
admin.site.site_title = "MaiLou Cloud"
admin.site.index_title = "Dashboard"

# O TRUQUE ESTÁ AQUI:
# Ao definir site_url como None, o Django remove o link "Início" / "Ver o Site"
admin.site.site_url = None 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    
    path('clientes/', include('apps.clientes.urls')),
    path('', include('apps.backups.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)