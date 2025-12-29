from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.functions import Lower  # <--- Importe isso para ordenar ignorando maiúsculas
from apps.clientes.models import Cliente
from .models import ValidacaoBackup
from .forms import ValidacaoForm

@login_required
def dashboard(request):
    """
    View principal que agrega dados de clientes e validações.
    """
    # ALTERAÇÃO AQUI: Adicionado .order_by(Lower('nome_fantasia'))
    clientes = Cliente.objects.filter(ativo=True).order_by(Lower('nome_fantasia'))
    
    ultimas_validacoes = ValidacaoBackup.objects.select_related(
        'rotina', 'rotina__ferramenta', 'usuario'
    ).all()[:15]
    
    return render(request, 'dashboard.html', {
        'clientes': clientes,
        'ultimas_validacoes': ultimas_validacoes
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