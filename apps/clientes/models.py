from django.db import models
from apps.common.models import TimeStampedModel

class Cliente(TimeStampedModel):
    razao_social = models.CharField(max_length=200)
    nome_fantasia = models.CharField(max_length=150)
    cnpj = models.CharField(max_length=18, unique=True)
    contato_tecnico = models.CharField(max_length=100)
    email_contato = models.EmailField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome_fantasia

class Servidor(TimeStampedModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='servidores')
    hostname = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    sistema_operacional = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return f"{self.hostname} ({self.cliente.nome_fantasia})"