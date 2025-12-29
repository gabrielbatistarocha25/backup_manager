from django import forms
from .models import ValidacaoBackup

class ValidacaoForm(forms.ModelForm):
    class Meta:
        model = ValidacaoBackup
        fields = ['rotina', 'status', 'observacao', 'evidencia']
        widgets = {
            'observacao': forms.Textarea(attrs={'rows': 3, 'class': 'w-full p-2 border rounded mt-1'}),
            'status': forms.Select(attrs={'class': 'w-full p-2 border rounded mt-1'}),
            'rotina': forms.Select(attrs={'class': 'w-full p-2 border rounded mt-1'}),
            'evidencia': forms.FileInput(attrs={'class': 'w-full p-2 border rounded mt-1'}),
        }
    
    def __init__(self, cliente_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cliente_id:
            # Filtra rotinas apenas dos servidores daquele cliente
            self.fields['rotina'].queryset = self.fields['rotina'].queryset.filter(
                servidores__cliente_id=cliente_id
            ).distinct()