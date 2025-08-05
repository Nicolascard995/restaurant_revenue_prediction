#!/usr/bin/env python3
"""
Test para el sistema de caché inteligente de PDFs
"""

import os
import sys
import tempfile
import time
from pathlib import Path

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_cache_manager import PDFCacheManager, PDFAnalysis
from datetime import datetime

def test_cache_system():
    """Test del sistema de caché de PDFs"""
    print("🚀 Probando sistema de caché inteligente de PDFs...")
    print("=" * 60)
    
    # Crear directorio temporal para tests
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = os.path.join(temp_dir, "cache")
        db_path = os.path.join(temp_dir, "test_cache.db")
        
        # Inicializar caché
        cache = PDFCacheManager(cache_dir=cache_dir, db_path=db_path)
        
        # Test 1: Verificar inicialización
        print("📊 Probando inicialización del caché...")
        assert os.path.exists(cache_dir), "Directorio de caché no creado"
        assert os.path.exists(db_path), "Base de datos no creada"
        print("✅ Inicialización exitosa")
        
        # Test 2: Crear análisis de prueba
        print("📄 Probando guardado de análisis...")
        test_analysis = PDFAnalysis(
            file_id="test_123",
            filename="test_document.pdf",
            file_hash="abc123hash",
            analysis_date=datetime.now().isoformat(),
            analysis_data={
                "datos_demograficos": {"poblacion": 1000000},
                "competencia": {"restaurantes": 50},
                "indicadores_economicos": {"pib": 5000000000}
            },
            tokens_used=150,
            processing_time=2.5,
            status="completed"
        )
        
        cache.save_analysis(test_analysis)
        print("✅ Análisis guardado exitosamente")
        
        # Test 3: Verificar estadísticas
        print("📈 Probando estadísticas del caché...")
        stats = cache.get_analysis_stats()
        assert stats["total_analyses"] == 1, "No se contó el análisis"
        assert stats["successful_analyses"] == 1, "No se contó el análisis exitoso"
        assert stats["total_tokens_used"] == 150, "No se contaron los tokens"
        print("✅ Estadísticas correctas")
        
        # Test 4: Verificar recuperación de análisis
        print("🔍 Probando recuperación de análisis...")
        # Crear archivo temporal para simular PDF
        test_file_path = os.path.join(temp_dir, "test_document.pdf")
        with open(test_file_path, "w") as f:
            f.write("Contenido de prueba")
        
        # Simular hash del archivo
        cached_analysis = cache.get_cached_analysis(test_file_path)
        # Como el hash no coincide, debería ser None
        assert cached_analysis is None, "No debería encontrar análisis para hash diferente"
        print("✅ Recuperación de análisis correcta")
        
        # Test 5: Verificar análisis recientes
        print("📋 Probando análisis recientes...")
        recent_analyses = cache.get_recent_analyses(limit=5)
        assert len(recent_analyses) == 1, "No se encontró el análisis reciente"
        assert recent_analyses[0].file_id == "test_123", "ID de archivo incorrecto"
        print("✅ Análisis recientes correctos")
        
        # Test 6: Verificar limpieza de análisis antiguos
        print("🗑️ Probando limpieza de análisis antiguos...")
        # Crear análisis antiguo
        old_analysis = PDFAnalysis(
            file_id="old_123",
            filename="old_document.pdf",
            file_hash="oldhash",
            analysis_date=(datetime.now().replace(year=2020)).isoformat(),  # 3 años atrás
            analysis_data={},
            tokens_used=100,
            processing_time=1.0,
            status="completed"
        )
        cache.save_analysis(old_analysis)
        
        # Verificar que hay 2 análisis
        stats_before = cache.get_analysis_stats()
        assert stats_before["total_analyses"] == 2, "No se guardó el análisis antiguo"
        
        # Limpiar análisis antiguos
        cache.clear_old_analyses(days=30)
        
        # Verificar que solo queda 1 análisis
        stats_after = cache.get_analysis_stats()
        assert stats_after["total_analyses"] == 1, "No se limpió el análisis antiguo"
        print("✅ Limpieza de análisis antiguos correcta")
        
        print("\n" + "=" * 60)
        print("🎉 ¡TODOS LOS TESTS DEL SISTEMA DE CACHÉ PASARON!")
        print("✅ El sistema de caché está funcionando correctamente")
        print("=" * 60)
        
        return True

if __name__ == "__main__":
    try:
        success = test_cache_system()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error en los tests del caché: {e}")
        exit(1) 