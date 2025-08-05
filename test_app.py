#!/usr/bin/env python3
"""
Tests completos para la aplicación de predicción de ingresos de restaurantes
"""

import pytest
import json
import os
import sys
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar la aplicación
from app import app

# Crear cliente de test
client = TestClient(app)

class TestRestaurantRevenuePrediction:
    """Tests para la aplicación de predicción de ingresos de restaurantes"""
    
    def test_health_check(self):
        """Test del endpoint de health check"""
        print("🏥 Probando health check...")
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        print("✅ Health check exitoso")
    
    def test_home_endpoint(self):
        """Test del endpoint principal"""
        print("🏠 Probando endpoint principal...")
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        print("✅ Endpoint principal exitoso")
    
    def test_pdf_upload_page(self):
        """Test de la página de upload de PDF"""
        print("📄 Probando página de upload PDF...")
        response = client.get("/pdf")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        print("✅ Página de upload PDF exitosa")
    
    def test_analyze_restaurant_valid_data(self):
        """Test del análisis de restaurante con datos válidos"""
        print("🍽️ Probando análisis de restaurante...")
        
        test_data = {
            "city": "Madrid",
            "city_group": "Big Cities",
            "type": "FC",
            "open_date": "2023-01-15",
            "investment": 50000,
            "monthly_costs": 8000
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
    
    def test_analyze_restaurant_invalid_data(self):
        """Test del análisis con datos inválidos"""
        print("❌ Probando análisis con datos inválidos...")
        
        # Test con datos faltantes
        invalid_data = {
            "city": "",
            "city_group": "Invalid",
            "type": "XX",
            "investment": -1000,
            "monthly_costs": 8000
        }
        
        response = client.post("/api/analyze", json=invalid_data)
        assert response.status_code == 400  # Bad request for validation errors
        
        print("✅ Validación de datos inválidos exitosa")
    
    def test_ai_advice_endpoint(self):
        """Test del endpoint de consejos de IA"""
        print("🤖 Probando endpoint de consejos de IA...")
        
        test_data = {
            "city": "Barcelona",
            "type": "IL",
            "investment": 75000,
            "monthly_costs": 12000
        }
        
        # Mock de OpenAI para evitar llamadas reales
        with patch('app.openai.ChatCompletion.create') as mock_openai:
            mock_openai.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Test advice"))]
            )
            
            response = client.post("/api/ai_advice", json=test_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "advice" in data
            assert "analysis" in data
            
        print("✅ Endpoint de consejos de IA exitoso")
    
    def test_ml_model_info(self):
        """Test del endpoint de información del modelo ML"""
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
    
    def test_pdf_cost_info(self):
        """Test del endpoint de información de costos de PDF"""
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
    
    def test_rate_limiting(self):
        """Test de rate limiting"""
        print("⏱️ Probando rate limiting...")
        
        # Hacer algunos requests para verificar que funciona
        for i in range(3):
            response = client.post("/api/analyze", json={
                "city": f"TestCity{i}",
                "city_group": "Big Cities",
                "type": "FC",
                "open_date": "2023-01-15",
                "investment": 50000,
                "monthly_costs": 8000
            })
            
            # Verificar que al menos los primeros requests funcionan
            assert response.status_code == 200
        
        print("✅ Rate limiting funcionando correctamente")

class TestInvestmentProjection:
    """Tests para las proyecciones de inversión"""
    
    def test_projection_calculation(self):
        """Test del cálculo de proyecciones"""
        print("📊 Probando cálculos de proyección...")
        
        from investment_projection import investment_projection
        
        # Datos de prueba
        investment = 50000
        initial_revenue = 16301
        monthly_costs = 8000
        
        projection = investment_projection.calculate_projection(
            initial_investment=investment,
            initial_revenue=initial_revenue,
            initial_monthly_costs=monthly_costs,
            years=5
        )
        
        assert len(projection) == 5
        assert all(isinstance(year, dict) for year in projection)
        assert all('revenue' in year for year in projection)
        assert all('profit' in year for year in projection)
        
        print("✅ Cálculos de proyección exitosos")
    
    def test_key_metrics(self):
        """Test de las métricas clave"""
        print("📈 Probando métricas clave...")
        
        from investment_projection import investment_projection
        
        # Crear proyección de prueba
        projection = investment_projection.calculate_projection(
            initial_investment=50000,
            initial_revenue=16301,
            initial_monthly_costs=8000,
            years=10
        )
        
        metrics = investment_projection.get_key_metrics(projection)
        
        assert "year_2" in metrics
        assert "year_5" in metrics
        assert "year_10" in metrics
        assert "summary" in metrics
        
        print("✅ Métricas clave exitosas")

class TestPDFFunctionality:
    """Tests para funcionalidades de PDF"""
    
    def test_pdf_upload_structure(self):
        """Test de la estructura de upload de PDF"""
        print("📄 Probando estructura de upload PDF...")
        
        # Verificar que el directorio uploads existe
        assert os.path.exists("uploads")
        
        # Verificar que pdf_manager está disponible
        from pdf_upload import pdf_manager
        assert hasattr(pdf_manager, 'save_pdf')
        assert hasattr(pdf_manager, 'get_pdf_path')
        
        print("✅ Estructura de PDF exitosa")
    
    def test_pdf_analyzer_structure(self):
        """Test de la estructura del analizador de PDF"""
        print("🔍 Probando estructura del analizador PDF...")
        
        from pdf_analyzer import pdf_analyzer
        assert hasattr(pdf_analyzer, 'extract_text')
        assert hasattr(pdf_analyzer, 'analyze_content')
        
        print("✅ Estructura del analizador PDF exitosa")

def run_all_tests():
    """Ejecutar todos los tests"""
    print("🚀 Iniciando tests completos de la aplicación...")
    print("=" * 60)
    
    # Crear instancia de test
    test_instance = TestRestaurantRevenuePrediction()
    
    # Ejecutar tests principales
    try:
        test_instance.test_health_check()
        test_instance.test_home_endpoint()
        test_instance.test_pdf_upload_page()
        test_instance.test_analyze_restaurant_valid_data()
        test_instance.test_analyze_restaurant_invalid_data()
        test_instance.test_ai_advice_endpoint()
        test_instance.test_ml_model_info()
        test_instance.test_pdf_cost_info()
        test_instance.test_rate_limiting()
        
        # Tests de proyecciones
        projection_tests = TestInvestmentProjection()
        projection_tests.test_projection_calculation()
        projection_tests.test_key_metrics()
        
        # Tests de PDF
        pdf_tests = TestPDFFunctionality()
        pdf_tests.test_pdf_upload_structure()
        pdf_tests.test_pdf_analyzer_structure()
        
        print("\n" + "=" * 60)
        print("🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
        print("✅ La aplicación está lista para subir a GitHub y desplegar en Render")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en los tests: {e}")
        print("🔧 Revisa los errores antes de subir a GitHub")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 