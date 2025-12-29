from django.db import models

class TimeStampedModel(models.Model):
    """
    Modelo abstrato que adiciona campos created_at e updated_at
    automaticamente a qualquer tabela que herdar dele.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        abstract = True