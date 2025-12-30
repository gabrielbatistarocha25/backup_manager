from django import forms
from .models import ValidacaoBackup

class ValidacaoForm(forms.ModelForm):
    class Meta:
        model = ValidacaoBackup
        fields = ['rotina', 'status', 'observacao', 'evidencia']
        
        # DEFINIÇÃO DE ESTILOS (IGUAL AO UNFOLD ADMIN)
        # Classes: borda suave, texto escuro, foco azul, transição suave
        widgets = {
            'rotina': forms.Select(attrs={
                'class': 'w-full bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5 transition duration-150 ease-in-out'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5 transition duration-150 ease-in-out'
            }),
            'evidencia': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none focus:border-blue-500 focus:ring-blue-500',
                'accept': '.txt,.jpg,.jpeg,.png'  # <--- NOVA LINHA: Filtra na janela do OS
            }),
            'observacao': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'block p-2.5 w-full text-sm text-gray-900 bg-white rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out',
                'placeholder': 'Descreva qualquer anomalia encontrada...'
            }),
        }
    
    def __init__(self, cliente_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cliente_id:
            # Mantém a lógica de filtrar rotinas apenas do cliente
            self.fields['rotina'].queryset = self.fields['rotina'].queryset.filter(
                servidores__cliente_id=cliente_id
            ).distinct()
            # Personaliza a label vazia do select
            self.fields['rotina'].empty_label = "Selecione uma rotina..."