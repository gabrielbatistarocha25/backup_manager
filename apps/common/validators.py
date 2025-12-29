import os
import uuid
import magic
from django.core.exceptions import ValidationError

def validate_file_infection(file):
    """
    Valida o tipo real do arquivo (MIME sniffing) para prevenir
    uploads maliciosos renomeados (ex: exe renomeado para jpg).
    """
    valid_mime_types = [
        'image/jpeg', 'image/png', 'application/pdf', 'text/plain'
    ]
    
    # Lê os primeiros 2KB para identificar o cabeçalho (magic number)
    file_header = file.read(2048)
    file_mime_type = magic.from_buffer(file_header, mime=True)
    file.seek(0) # Retorna o cursor para o início

    if file_mime_type not in valid_mime_types:
        raise ValidationError(f"Tipo de arquivo não permitido: {file_mime_type}. Use PDF, Imagem ou TXT.")

def evidence_upload_path(instance, filename):
    """
    Renomeia o arquivo para um UUID mantendo a extensão.
    Evita Path Traversal e sobrescrita de arquivos.
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('evidencias/', filename)