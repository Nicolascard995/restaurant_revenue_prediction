#!/usr/bin/env python3
"""
Test para el sistema de idiomas y traducción automática
"""

import os
import sys
from fastapi.testclient import TestClient

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar la aplicación
from app import app

# Crear cliente de test
client = TestClient(app)

def test_language_system():
    """Test del sistema de idiomas y traducción"""
    print("🌍 Probando sistema de idiomas y traducción...")
    print("=" * 60)
    
    # Test 1: Obtener idiomas disponibles
    print("🏳️ Probando endpoint de idiomas...")
    response = client.get("/api/languages")
    assert response.status_code == 200
    
    data = response.json()
    assert "success" in data
    assert "languages" in data
    assert data["success"] == True
    
    languages = data["languages"]["available_languages"]
    assert len(languages) == 3, "Debe haber 3 idiomas"
    
    language_codes = [lang["code"] for lang in languages]
    assert "en" in language_codes, "Inglés debe estar incluido"
    assert "es" in language_codes, "Español debe estar incluido"
    assert "de" in language_codes, "Alemán debe estar incluido"
    
    print("✅ Endpoint de idiomas exitoso")
    
    # Test 2: Análisis en inglés (idioma por defecto)
    print("🇺🇸 Probando análisis en inglés...")
    test_data_en = {
        "country": "Germany",
        "city": "Berlin",
        "city_group": "Big Cities",
        "type": "FC",
        "open_date": "2023-01-15",
        "investment": 500000,
        "monthly_costs": 25000,
        "language": "en"
    }
    
    response = client.post("/api/analyze", json=test_data_en)
    assert response.status_code == 200
    
    data = response.json()
    assert "success" in data
    assert "revenue_estimate" in data
    assert "viability_analysis" in data
    assert data["success"] == True
    
    print("✅ Análisis en inglés exitoso")
    
    # Test 3: Análisis en español
    print("🇪🇸 Probando análisis en español...")
    test_data_es = {
        "country": "Argentina",
        "city": "Buenos Aires",
        "city_group": "Big Cities",
        "type": "IL",
        "open_date": "2023-01-15",
        "investment": 150000,
        "monthly_costs": 12000,
        "language": "es"
    }
    
    response = client.post("/api/analyze", json=test_data_es)
    assert response.status_code == 200
    
    data = response.json()
    assert "success" in data
    assert "revenue_estimate" in data
    assert "viability_analysis" in data
    assert data["success"] == True
    
    print("✅ Análisis en español exitoso")
    
    # Test 4: Análisis en alemán
    print("🇩🇪 Probando análisis en alemán...")
    test_data_de = {
        "country": "Germany",
        "city": "Munich",
        "city_group": "Big Cities",
        "type": "FC",
        "open_date": "2023-01-15",
        "investment": 400000,
        "monthly_costs": 30000,
        "language": "de"
    }
    
    response = client.post("/api/analyze", json=test_data_de)
    assert response.status_code == 200
    
    data = response.json()
    assert "success" in data
    assert "revenue_estimate" in data
    assert "viability_analysis" in data
    assert data["success"] == True
    
    print("✅ Análisis en alemán exitoso")
    
    # Test 5: Validación de idioma inválido
    print("❌ Probando validación de idioma inválido...")
    invalid_language_data = {
        "country": "Germany",
        "city": "Berlin",
        "city_group": "Big Cities",
        "type": "FC",
        "open_date": "2023-01-15",
        "investment": 500000,
        "monthly_costs": 25000,
        "language": "fr"  # Idioma no válido
    }
    
    response = client.post("/api/analyze", json=invalid_language_data)
    assert response.status_code == 400  # Debe fallar con idioma inválido
    
    print("✅ Validación de idioma inválido exitosa")
    
    # Test 6: Análisis sin especificar idioma (debe usar inglés por defecto)
    print("🇺🇸 Probando análisis sin especificar idioma...")
    default_language_data = {
        "country": "Mexico",
        "city": "Mexico City",
        "city_group": "Big Cities",
        "type": "IL",
        "open_date": "2023-01-15",
        "investment": 200000,
        "monthly_costs": 15000
        # Sin campo language, debe usar "en" por defecto
    }
    
    response = client.post("/api/analyze", json=default_language_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "success" in data
    assert data["success"] == True
    
    print("✅ Análisis con idioma por defecto exitoso")
    
    print("\n" + "=" * 60)
    print("🎉 ¡TODOS LOS TESTS DEL SISTEMA DE IDIOMAS PASARON!")
    print("✅ El sistema de idiomas y traducción está funcionando correctamente")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_language_system()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error en los tests del sistema de idiomas: {e}")
        exit(1) 