import os
import uuid
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2
import pdfplumber
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)

class PDFUploadManager:
    def __init__(self, upload_dir: str = "uploads/pdfs"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {'.pdf'}
    
    async def upload_pdf(self, file: UploadFile) -> Dict[str, Any]:
        """Carga y valida un archivo PDF"""
        try:
            # Validar extensión
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
            
            # Validar tamaño
            if file.size and file.size > self.max_file_size:
                raise HTTPException(status_code=400, detail="Archivo demasiado grande. Máximo 10MB")
            
            # Generar nombre único
            file_id = str(uuid.uuid4())
            filename = f"{file_id}_{file.filename}"
            file_path = self.upload_dir / filename
            
            # Guardar archivo
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Extraer texto básico
            text_content = self._extract_text(file_path)
            
            return {
                "file_id": file_id,
                "filename": file.filename,
                "file_path": str(file_path),
                "size": len(content),
                "text_content": text_content[:1000],  # Primeros 1000 caracteres
                "status": "uploaded"
            }
            
        except Exception as e:
            logger.error(f"Error al cargar PDF: {e}")
            raise HTTPException(status_code=500, detail="Error al procesar el archivo")
    
    def _extract_text(self, file_path: Path) -> str:
        """Extrae texto del PDF usando múltiples métodos"""
        text = ""
        
        try:
            # Método 1: PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            # Si no hay texto, intentar con pdfplumber
            if not text.strip():
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            
        except Exception as e:
            logger.warning(f"Error al extraer texto: {e}")
            text = "No se pudo extraer texto del PDF"
        
        return text
    
    def get_pdf_info(self, file_path: str) -> Dict[str, Any]:
        """Obtiene información básica del PDF"""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError("Archivo no encontrado")
            
            with open(path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                return {
                    "pages": len(pdf_reader.pages),
                    "file_size": path.stat().st_size,
                    "filename": path.name
                }
                
        except Exception as e:
            logger.error(f"Error al obtener info del PDF: {e}")
            return {"error": str(e)}
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Limpia archivos antiguos"""
        import time
        current_time = time.time()
        
        for file_path in self.upload_dir.glob("*.pdf"):
            if current_time - file_path.stat().st_mtime > max_age_hours * 3600:
                try:
                    file_path.unlink()
                    logger.info(f"Archivo eliminado: {file_path}")
                except Exception as e:
                    logger.error(f"Error al eliminar archivo: {e}")

# Instancia global
pdf_manager = PDFUploadManager() 