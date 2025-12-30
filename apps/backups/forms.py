from django import forms
from .models import ValidacaoBackup, RotinaBackup

class ValidacaoForm(forms.ModelForm):
    class Meta:
        model = ValidacaoBackup
        fields = ['rotina', 'status', 'observacao', 'evidencia']
        
        widgets = {
            # RadioSelect permite que a gente renderize as opções como botões no template
            'status': forms.RadioSelect(attrs={'class': 'peer sr-only'}),
            'observacao': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, cliente_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Filtra as rotinas apenas do cliente atual
        if cliente_id:
            self.fields['rotina'].queryset = RotinaBackup.objects.filter(cliente_id=cliente_id)
            
        # 2. Estilização do Campo Rotina (Dropdown)
        self.fields['rotina'].widget.attrs.update({
            'class': 'w-full appearance-none rounded-lg border-gray-300 bg-gray-50 p-3 pr-8 focus:border-blue-500 focus:ring-blue-500 transition cursor-pointer'
        })
        self.fields['rotina'].empty_label = "Selecione a rotina na lista..."

        # 3. Estilização do Campo Evidência (Input Oculto para funcionar com Drag & Drop)
        self.fields['evidencia'].widget.attrs.update({
            'class': 'hidden',
            'id': 'file-upload',
            # Mantemos o accept para ajudar o navegador, mas a segurança real é no backend (validators.py)
            'accept': '.txt,.jpg,.jpeg,.png'
        })