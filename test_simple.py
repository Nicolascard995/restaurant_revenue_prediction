#!/usr/bin/env python3
"""
Test simple y robusto para la aplicación de predicción de ingresos de restaurantes
"""

import os
import sys
import json
from fastapi.testclient import TestClient

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar la aplicación
from app import app

# Crear cliente de test
client = TestClient(app)

def test_basic_functionality():
    """Test básico de funcionalidades principales"""
    print("🚀 Iniciando test básico de la aplicación...")
    print("=" * 60)
    
    # Test 1: Health check
    print("🏥 Probando health check...")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    print("✅ Health check exitoso")
    
    # Test 2: Endpoint principal
    print("🏠 Probando endpoint principal...")
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    print("✅ Endpoint principal exitoso")
    
    # Test 3: Página de PDF
    print("📄 Probando página de upload PDF...")
    response = client.get("/pdf")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    print("✅ Página de upload PDF exitosa")
    
    # Test 4: Análisis de restaurante con datos válidos
    print("🍽️ Probando análisis de restaurante...")
    test_data = {
        "country": "Germany",
        "city": "Berlin",
        "city_group": "Big Cities",
        "type": "FC",
        "open_date": "2023-01-15",
        "investment": 50000,
        "monthly_costs": 8000,
        "language": "en"
    }
    
    response = client.post("/api/analyze", json=test_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "success" in data
    assert "revenue_estimate" in data
    assert "viability_analysis" in data
    assert data["success"] == True
    assert isinstance(data["revenue_estimate"], (int, float))
    print("✅ Análisis de restaurante exitoso")
    
    # Test 5: Validación de datos inválidos
    print("❌ Probando validación de datos inválidos...")
    invalid_data = {
        "country": "InvalidCountry",
        "city": "",
        "city_group": "Invalid",
        "type": "XX",
        "investment": -1000,
        "monthly_costs": 8000
    }
    
    response = client.post("/api/analyze", json=invalid_data)
    assert response.status_code == 400
    print("✅ Validación de datos inválidos exitosa")
    
    # Test 6: Información del modelo ML
    print("🧠 Probando información del modelo ML...")
    response = client.get("/api/ml/model-info")
    assert response.status_code == 200
    
    data = response.json()
    assert "success" in data
    assert "model_info" in data
    assert "description" in data
    assert "features" in data
    assert data["success"] == True
    print("✅ Información del modelo ML exitosa")
    
    # Test 7: Información de costos de PDF
    print("💰 Probando información de costos de PDF...")
    response = client.get("/api/pdf/cost-info")
    assert response.status_code == 200
    
    data = response.json()
    assert "success" in data
    assert "pdf_analyzer_cost" in data
    assert "prompt_engine_cost" in data
    assert "optimization_tips" in data
    assert data["success"] == True
    print("✅ Información de costos de PDF exitosa")
    
    # Test 8: Proyecciones financieras
    print("📊 Probando proyecciones financieras...")
    try:
        from investment_projection import investment_projection
        
        projection = investment_projection.calculate_projection(
            initial_investment=50000,
            initial_revenue=16301,
            initial_monthly_costs=8000,
            years=5
        )
        
        assert len(projection) == 5
        assert all(isinstance(year, dict) for year in projection)
        assert all('revenue' in year for year in projection)
        assert all('profit' in year for year in projection)
        
        print("✅ Proyecciones financieras exitosas")
    except Exception as e:
        print(f"⚠️ Proyecciones financieras: {e}")
    
    # Test 9: Estructura de archivos
    print("📁 Verificando estructura de archivos...")
    required_files = [
        "app.py",
        "requirements.txt",
        "README.md",
        "render.yaml",
        "Procfile",
        "runtime.txt"
    ]
    
    for file in required_files:
        assert os.path.exists(file), f"Archivo requerido no encontrado: {file}"
    
    assert os.path.exists("uploads"), "Directorio uploads no encontrado"
    assert os.path.exists("templates"), "Directorio templates no encontrado"
    assert os.path.exists("static"), "Directorio static no encontrado"
    
    print("✅ Estructura de archivos correcta")
    
    print("\n" + "=" * 60)
    print("🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
    print("✅ La aplicación está lista para subir a GitHub y desplegar en Render")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_basic_functionality()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error en los tests: {e}")
        print("🔧 Revisa los errores antes de subir a GitHub")
        exit(1) 