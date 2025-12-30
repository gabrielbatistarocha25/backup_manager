from django import forms
from .models import ValidacaoBackup, RotinaBackup

class ValidacaoForm(forms.ModelForm):
    class Meta:
        model = ValidacaoBackup
        fields = ['rotina', 'status', 'observacao', 'evidencia']
        
        widgets = {
            # Status como RadioSelect para os botões grandes
            'status': forms.RadioSelect(attrs={'class': 'peer sr-only'}),
            
            'observacao': forms.Textarea(attrs={
                'rows': 3,
                'class': (
                    'block p-2.5 w-full text-sm rounded-lg border transition duration-150 ease-in-out '
                    'text-gray-900 bg-white border-gray-300 focus:ring-blue-500 focus:border-blue-500 '
                    'dark:bg-slate-800 dark:border-slate-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
                ),
                'placeholder': 'Descreva qualquer anomalia encontrada...'
            }),
            
            # AQUI ESTÁ A VALIDAÇÃO DO NAVEGADOR (Extensão)
            'evidencia': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'file-upload',
                'accept': '.txt,.jpg,.jpeg,.png'  # <--- Garante que o navegador filtre os arquivos
            }),
        }
    
    def __init__(self, cliente_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if cliente_id:
            self.fields['rotina'].queryset = RotinaBackup.objects.filter(cliente_id=cliente_id)
            
        self.fields['rotina'].empty_label = "Selecione uma rotina..."
        
        # Estilo Dark Mode para o Select
        self.fields['rotina'].widget.attrs.update({
            'class': (
                'w-full appearance-none rounded-lg border p-3 pr-8 transition cursor-pointer '
                'bg-gray-50 border-gray-300 text-gray-900 focus:ring-blue-500 focus:border-blue-500 '
                'dark:bg-slate-800 dark:border-slate-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
            )
        })