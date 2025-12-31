import os
import uuid
import magic
from django.core.exceptions import ValidationError
import re
from django.core.exceptions import ValidationError

def validate_file_infection(file):
    """
    Valida tamanho, extensão e tipo real (MIME) do arquivo.
    """
    # 1. Configurações
    MAX_SIZE_MB = 5
    VALID_MIME_TYPES = [
        'image/jpeg', 
        'image/png', 
        'text/plain'
    ]
    VALID_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.txt']

    # 2. Validação de Tamanho
    if file.size > MAX_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"O arquivo é muito grande ({file.size/1024/1024:.1f}MB). O limite máximo é {MAX_SIZE_MB}MB.")

    # 3. Validação de Extensão
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in VALID_EXTENSIONS:
        raise ValidationError("Extensão não permitida. Use apenas: .txt, .jpg ou .png")

    # 4. Validação de Conteúdo Real (Magic Numbers)
    # Lê o início do arquivo para garantir que não é um .exe renomeado
    initial_pos = file.tell()
    file.seek(0)
    mime_type = magic.from_buffer(file.read(2048), mime=True)
    file.seek(initial_pos) # Reseta o ponteiro do arquivo

    if mime_type not in VALID_MIME_TYPES:
        raise ValidationError(f"Conteúdo do arquivo inválido ({mime_type}). Envie apenas Logs de texto ou Imagens.")

def evidence_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('evidencias/', filename)

