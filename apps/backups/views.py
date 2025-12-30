from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from apps.clientes.models import Cliente
from .models import ValidacaoBackup
from .forms import ValidacaoForm
from django.http import JsonResponse
from apps.clientes.models import Servidor

@login_required
def dashboard(request):
    """
    VISÃO NOC: Clientes e seus status recentes.
    """
    clientes = Cliente.objects.filter(ativo=True).order_by(Lower('nome_fantasia'))
    
    for cliente in clientes:
        cliente.historico_recente = ValidacaoBackup.objects.filter(
            rotina__servidores__cliente=cliente
        ).select_related('rotina', 'usuario').order_by('-created_at')[:5]

        if cliente.historico_recente:
            cliente.ultimo_status = cliente.historico_recente[0].status
        else:
            cliente.ultimo_status = 'PENDENTE'

    ultimas_globais = ValidacaoBackup.objects.select_related(
        'rotina', 'rotina__ferramenta', 'usuario'
    ).all()[:10]
    
    return render(request, 'dashboard.html', {
        'clientes': clientes,
        'ultimas_validacoes': ultimas_globais
    })

@login_required
def historico_global(request):
    """
    VISÃO AUDITORIA: Lista plana e paginada.
    CORREÇÃO: Usamos prefetch_related para a relação ManyToMany de servidores.
    """
    validacoes_list = ValidacaoBackup.objects.select_related(
        'rotina', 
        'rotina__ferramenta', 
        'usuario'
    ).prefetch_related(
        'rotina__servidores__cliente' # <--- CORREÇÃO AQUI (Mudou de select para prefetch)
    ).all().order_by('-created_at')

    paginator = Paginator(validacoes_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'historico_global.html', {
        'page_obj': page_obj
    })

@login_required
def nova_validacao(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        form = ValidacaoForm(cliente_id, request.POST, request.FILES)
        if form.is_valid():
            validacao = form.save(commit=False)
            validacao.usuario = request.user
            validacao.save()
            messages.success(request, 'Backup validado com sucesso!')
            return redirect('dashboard')
    else:
        form = ValidacaoForm(cliente_id=cliente.id)

    return render(request, 'validacao_form.html', {
        'form': form, 
        'cliente': cliente
    })

@login_required
def get_servidores_por_cliente(request):
    """
    Retorna JSON com os servidores de um cliente específico.
    Usado no Admin para filtrar o combo de seleção.
    """
    cliente_id = request.GET.get('cliente_id')
    if not cliente_id:
        return JsonResponse({'servidores': []})
    
    servidores = Servidor.objects.filter(cliente_id=cliente_id).values('id', 'hostname', 'descricao')
    return JsonResponse({'servidores': list(servidores)})