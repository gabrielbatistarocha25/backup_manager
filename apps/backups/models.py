from django.db import models
from django.contrib.auth.models import User
from apps.common.models import TimeStampedModel
from apps.common.validators import evidence_upload_path, validate_file_infection

class FerramentaBackup(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nome

class RotinaBackup(TimeStampedModel):
    FREQUENCIA_CHOICES = [
        ('DIARIO', 'Diário'),
        ('SEMANAL', 'Semanal'),
        ('MENSAL', 'Mensal'),
    ]

    ferramenta = models.ForeignKey(FerramentaBackup, on_delete=models.PROTECT)
    descricao = models.CharField(max_length=200)
    # Referência cruzada Lazy para o app Clientes
    servidores = models.ManyToManyField('clientes.Servidor', related_name='rotinas')
    frequencia = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    horario_execucao = models.TimeField()
    retencao_dias = models.IntegerField()
    
    def __str__(self):
        return f"{self.ferramenta} - {self.descricao}"

class ValidacaoBackup(TimeStampedModel):
    STATUS_CHOICES = [
        ('SUCESSO', '✅ Sucesso'),
        ('ALERTA', '⚠️ Alerta'),
        ('ERRO', '❌ Erro'),
    ]

    rotina = models.ForeignKey(RotinaBackup, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='validacoes_realizadas')
    
    # Novo campo para rastrear quem editou (pode ser nulo se nunca foi editado)
    editado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='validacoes_editadas',
        verbose_name="Editado por"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    observacao = models.TextField(blank=True)
    evidencia = models.FileField(
        upload_to=evidence_upload_path, 
        validators=[validate_file_infection]
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Validação de Backup"
        verbose_name_plural = "Validações de Backup"

    def __str__(self):
        return f"Validação {self.id} - {self.status}"