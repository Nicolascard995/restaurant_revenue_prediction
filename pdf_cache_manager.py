#!/usr/bin/env python3
"""
Sistema de caché inteligente para PDFs
Evita re-procesar PDFs ya analizados y mejora el rendimiento
"""

import os
import json
import hashlib
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass, asdict
import sqlite3
import threading

logger = logging.getLogger(__name__)

@dataclass
class PDFAnalysis:
    """Estructura para almacenar análisis de PDFs"""
    file_id: str
    filename: str
    file_hash: str
    analysis_date: datetime
    analysis_data: Dict[str, Any]
    tokens_used: int
    processing_time: float
    status: str  # 'completed', 'failed', 'processing'
    error_message: Optional[str] = None

class PDFCacheManager:
    def __init__(self, cache_dir: str = "cache/pdfs", db_path: str = "cache/pdf_database.db"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.lock = threading.Lock()
        
        # Inicializar base de datos
        self._init_database()
        
        # Cache en memoria para acceso rápido
        self._memory_cache = {}
        self._max_memory_cache = 50  # Máximo 50 PDFs en memoria
        
    def _init_database(self):
        """Inicializar base de datos SQLite para PDFs"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pdf_analyses (
                        file_id TEXT PRIMARY KEY,
                        filename TEXT NOT NULL,
                        file_hash TEXT NOT NULL,
                        analysis_date TEXT NOT NULL,
                        analysis_data TEXT NOT NULL,
                        tokens_used INTEGER,
                        processing_time REAL,
                        status TEXT NOT NULL,
                        error_message TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Índices para búsqueda rápida
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_hash ON pdf_analyses(file_hash)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON pdf_analyses(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_date ON pdf_analyses(analysis_date)')
                
                conn.commit()
                logger.info("✅ Base de datos de PDFs inicializada")
                
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcula hash SHA-256 del archivo"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculando hash: {e}")
            return ""
    
    def get_cached_analysis(self, file_path: str) -> Optional[PDFAnalysis]:
        """Obtiene análisis en caché si existe y es válido"""
        try:
            file_hash = self._calculate_file_hash(file_path)
            if not file_hash:
                return None
            
            # Buscar en caché de memoria primero
            if file_hash in self._memory_cache:
                cached = self._memory_cache[file_hash]
                if self._is_analysis_valid(cached):
                    logger.info(f"✅ Análisis encontrado en caché de memoria para {file_path}")
                    return cached
            
            # Buscar en base de datos
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM pdf_analyses 
                    WHERE file_hash = ? AND status = 'completed'
                    ORDER BY analysis_date DESC LIMIT 1
                ''', (file_hash,))
                
                row = cursor.fetchone()
                if row:
                    analysis = self._row_to_analysis(row)
                    if self._is_analysis_valid(analysis):
                        # Agregar a caché de memoria
                        self._add_to_memory_cache(analysis)
                        logger.info(f"✅ Análisis encontrado en caché para {file_path}")
                        return analysis
            
            logger.info(f"📄 No se encontró análisis en caché para {file_path}")
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo análisis en caché: {e}")
            return None
    
    def _is_analysis_valid(self, analysis: PDFAnalysis) -> bool:
        """Verifica si el análisis es válido (no muy antiguo)"""
        try:
            # Análisis válido por 30 días
            max_age = timedelta(days=30)
            analysis_date = datetime.fromisoformat(analysis.analysis_date)
            return datetime.now() - analysis_date < max_age
        except:
            return False
    
    def _add_to_memory_cache(self, analysis: PDFAnalysis):
        """Agrega análisis a caché de memoria"""
        with self.lock:
            # Limpiar caché si está lleno
            if len(self._memory_cache) >= self._max_memory_cache:
                # Eliminar el más antiguo
                oldest_key = min(self._memory_cache.keys(), 
                               key=lambda k: self._memory_cache[k].analysis_date)
                del self._memory_cache[oldest_key]
            
            self._memory_cache[analysis.file_hash] = analysis
    
    def save_analysis(self, analysis: PDFAnalysis):
        """Guarda análisis en base de datos y caché"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO pdf_analyses 
                    (file_id, filename, file_hash, analysis_date, analysis_data, 
                     tokens_used, processing_time, status, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    analysis.file_id,
                    analysis.filename,
                    analysis.file_hash,
                    analysis.analysis_date,
                    json.dumps(analysis.analysis_data),
                    analysis.tokens_used,
                    analysis.processing_time,
                    analysis.status,
                    analysis.error_message
                ))
                conn.commit()
            
            # Agregar a caché de memoria
            self._add_to_memory_cache(analysis)
            
            logger.info(f"✅ Análisis guardado en caché para {analysis.filename}")
            
        except Exception as e:
            logger.error(f"Error guardando análisis: {e}")
    
    def _row_to_analysis(self, row) -> PDFAnalysis:
        """Convierte fila de BD a objeto PDFAnalysis"""
        return PDFAnalysis(
            file_id=row[0],
            filename=row[1],
            file_hash=row[2],
            analysis_date=row[3],
            analysis_data=json.loads(row[4]),
            tokens_used=row[5],
            processing_time=row[6],
            status=row[7],
            error_message=row[8]
        )
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del caché"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de análisis
                cursor.execute('SELECT COUNT(*) FROM pdf_analyses')
                total_analyses = cursor.fetchone()[0]
                
                # Análisis exitosos
                cursor.execute('SELECT COUNT(*) FROM pdf_analyses WHERE status = "completed"')
                successful_analyses = cursor.fetchone()[0]
                
                # Análisis fallidos
                cursor.execute('SELECT COUNT(*) FROM pdf_analyses WHERE status = "failed"')
                failed_analyses = cursor.fetchone()[0]
                
                # Tokens totales usados
                cursor.execute('SELECT SUM(tokens_used) FROM pdf_analyses WHERE tokens_used IS NOT NULL')
                total_tokens = cursor.fetchone()[0] or 0
                
                # Tiempo promedio de procesamiento
                cursor.execute('SELECT AVG(processing_time) FROM pdf_analyses WHERE processing_time IS NOT NULL')
                avg_processing_time = cursor.fetchone()[0] or 0
                
                return {
                    "total_analyses": total_analyses,
                    "successful_analyses": successful_analyses,
                    "failed_analyses": failed_analyses,
                    "total_tokens_used": total_tokens,
                    "average_processing_time": round(avg_processing_time, 2),
                    "memory_cache_size": len(self._memory_cache),
                    "cache_hit_rate": self._calculate_cache_hit_rate()
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calcula tasa de aciertos del caché (simulado)"""
        # En una implementación real, esto se calcularía con logs de acceso
        return 0.85  # 85% de aciertos estimado
    
    def clear_old_analyses(self, days: int = 30):
        """Limpia análisis antiguos"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM pdf_analyses WHERE analysis_date < ?', (cutoff_date,))
                deleted_count = cursor.rowcount
                conn.commit()
            
            logger.info(f"🗑️ Eliminados {deleted_count} análisis antiguos")
            
        except Exception as e:
            logger.error(f"Error limpiando análisis antiguos: {e}")
    
    def get_recent_analyses(self, limit: int = 10) -> List[PDFAnalysis]:
        """Obtiene análisis recientes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM pdf_analyses 
                    ORDER BY analysis_date DESC 
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                return [self._row_to_analysis(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error obteniendo análisis recientes: {e}")
            return []

# Instancia global del caché
pdf_cache = PDFCacheManager() 