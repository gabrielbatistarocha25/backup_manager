from django.db import models
from django.contrib.auth.models import User
from apps.common.models import TimeStampedModel
from apps.common.validators import evidence_upload_path, validate_file_infection
# Importando o modelo Cliente para criar a chave estrangeira
from apps.clientes.models import Cliente, Servidor

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

    # NOVO CAMPO: Vincula a rotina ao cliente
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='rotinas', null=True, blank=True)
    
    ferramenta = models.ForeignKey(FerramentaBackup, on_delete=models.PROTECT, verbose_name="Ferramenta")
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    
    # Servidores continuam aqui, mas serão filtrados pelo cliente acima
    servidores = models.ManyToManyField(Servidor, related_name='rotinas', verbose_name="Servidores")
    
    frequencia = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES, verbose_name="Frequência")
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