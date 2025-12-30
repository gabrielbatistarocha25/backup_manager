from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from .models import RotinaBackup, ValidacaoBackup
from apps.clientes.models import Cliente, Servidor
from .forms import ValidacaoForm  # Importante: Mantendo o Form seguro

@login_required
def dashboard(request):
    # CORREÇÃO AQUI: Adicionado .order_by('nome_fantasia')
    clientes = Cliente.objects.filter(ativo=True).order_by('nome_fantasia').prefetch_related('servidores', 'rotinas')
    
    for cliente in clientes:
        # Pega a última validação de qualquer rotina deste cliente para definir o status do card
        ultima_validacao = ValidacaoBackup.objects.filter(
            rotina__cliente=cliente
        ).order_by('-created_at').first()
        
        cliente.ultimo_status = ultima_validacao.status if ultima_validacao else 'PENDENTE'
        
        # Histórico recente para o accordion (últimas 5)
        cliente.historico_recente = ValidacaoBackup.objects.filter(
            rotina__cliente=cliente
        ).select_related('rotina', 'rotina__ferramenta', 'usuario').order_by('-created_at')[:5]

    # Feed lateral (últimas 10 do sistema todo)
    ultimas_validacoes = ValidacaoBackup.objects.select_related(
        'rotina', 'rotina__ferramenta', 'rotina__cliente'
    ).order_by('-created_at')[:10]
    
    return render(request, 'dashboard.html', {
        'clientes': clientes,
        'ultimas_validacoes': ultimas_validacoes
    })

@login_required
def historico_global(request):
    # Mantendo a lógica de filtros e ordenação do histórico
    validacoes = ValidacaoBackup.objects.all().select_related(
        'rotina', 'rotina__ferramenta', 'rotina__cliente', 'usuario'
    )

    cliente_id = request.GET.get('cliente')
    status = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    ordenacao = request.GET.get('ordenacao', 'recente')

    if cliente_id:
        validacoes = validacoes.filter(rotina__cliente_id=cliente_id)
    if status:
        validacoes = validacoes.filter(status=status)
    if data_inicio:
        data_i = parse_date(data_inicio)
        if data_i:
            validacoes = validacoes.filter(created_at__date__gte=data_i)
    if data_fim:
        data_f = parse_date(data_fim)
        if data_f:
            validacoes = validacoes.filter(created_at__date__lte=data_f)

    mapa_ordenacao = {
        'recente': '-created_at',
        'antigo': 'created_at',
        'cliente_az': 'rotina__cliente__nome_fantasia',
        'cliente_za': '-rotina__cliente__nome_fantasia',
        'status': 'status',
    }
    campo_ordem = mapa_ordenacao.get(ordenacao, '-created_at')
    validacoes = validacoes.order_by(campo_ordem)

    clientes = Cliente.objects.filter(ativo=True).order_by('nome_fantasia')
    status_choices = ValidacaoBackup.STATUS_CHOICES

    context = {
        'validacoes': validacoes,
        'clientes': clientes,
        'status_choices': status_choices,
        'total_registros': validacoes.count(),
        'filtros_atuais': request.GET
    }
    return render(request, 'historico_global.html', context)

@login_required
def nova_validacao(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    
    # Lógica baseada em Formulário (Segura e Validada)
    if request.method == 'POST':
        form = ValidacaoForm(cliente_id, request.POST, request.FILES)
        
        if form.is_valid():
            validacao = form.save(commit=False)
            validacao.usuario = request.user
            validacao.save()
            return redirect('dashboard')
    else:
        form = ValidacaoForm(cliente_id=cliente_id)

    # Passamos rotinas também para caso de fallback no template
    rotinas = RotinaBackup.objects.filter(cliente=cliente)

    return render(request, 'nova_validacao.html', {
        'cliente': cliente,
        'form': form,      
        'rotinas': rotinas
    })

@login_required
def get_servidores_por_cliente(request):
    cliente_id = request.GET.get('cliente_id')
    if not cliente_id:
        return JsonResponse({'servidores': []})
    servidores = Servidor.objects.filter(cliente_id=cliente_id).values('id', 'hostname', 'descricao')
    return JsonResponse({'servidores': list(servidores)})