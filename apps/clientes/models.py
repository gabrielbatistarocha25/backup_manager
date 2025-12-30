from django.db import models
from apps.common.models import TimeStampedModel

class Cliente(TimeStampedModel):
    razao_social = models.CharField(max_length=200, verbose_name="Razão Social")
    nome_fantasia = models.CharField(max_length=150, verbose_name="Nome Fantasia")
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
    contato_tecnico = models.CharField(max_length=100, verbose_name="Contato")
    email_contato = models.EmailField(verbose_name="E-mail")
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome_fantasia

class Servidor(TimeStampedModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='servidores', verbose_name="Servidores")
    hostname = models.CharField(max_length=100, verbose_name="Hostname")
    ip_address = models.GenericIPAddressField(verbose_name="Endereço IP")
    sistema_operacional = models.CharField(max_length=100, verbose_name="Sistema Operacional")
    descricao = models.TextField(blank=True, verbose_name="Descrição")

    def __str__(self):
        return f"{self.hostname} ({self.cliente.nome_fantasia})"