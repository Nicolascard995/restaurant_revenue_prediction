#!/usr/bin/env python3
"""
Test para el sistema de países específicos (Alemania, Argentina, México)
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

def test_country_system():
    """Test del sistema de países específicos"""
    print("🌍 Probando sistema de países específicos...")
    print("=" * 60)
    
    # Test 1: Obtener países disponibles
    print("🏳️ Probando endpoint de países...")
    response = client.get("/api/countries")
    assert response.status_code == 200
    
    data = response.json()
    assert "success" in data
    assert "countries" in data
    assert data["success"] == True
    
    countries = data["countries"]
    assert len(countries) == 3, "Debe haber 3 países"
    
    country_codes = [c["code"] for c in countries]
    assert "Germany" in country_codes, "Alemania debe estar incluida"
    assert "Argentina" in country_codes, "Argentina debe estar incluida"
    assert "Mexico" in country_codes, "México debe estar incluida"
    
    print("✅ Endpoint de países exitoso")
    
    # Test 2: Obtener ciudades por país
    print("🏙️ Probando ciudades por país...")
    
    for country in ["Germany", "Argentina", "Mexico"]:
        response = client.get(f"/api/countries/{country}/cities")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "cities" in data
        assert data["success"] == True
        
        cities = data["cities"]
        assert len(cities) > 0, f"Debe haber ciudades para {country}"
        
        print(f"✅ Ciudades para {country}: {len(cities)} ciudades")
    
    # Test 3: Obtener insights por país
    print("📊 Probando insights por país...")
    
    for country in ["Germany", "Argentina", "Mexico"]:
        response = client.get(f"/api/countries/{country}/insights")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "insights" in data
        assert data["success"] == True
        
        insights = data["insights"]
        assert "country_name" in insights
        assert "currency" in insights
        assert "opportunities" in insights
        assert "risks" in insights
        
        print(f"✅ Insights para {country}: {insights['country_name']}")
    
    # Test 4: Análisis de restaurante con país específico
    print("🍽️ Probando análisis con países específicos...")
    
    test_data = {
        "country": "Germany",
        "city": "Berlin",
        "city_group": "Big Cities",
        "type": "FC",
        "open_date": "2023-01-15",
        "investment": 500000,
        "monthly_costs": 25000
    }
    
    response = client.post("/api/analyze", json=test_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "success" in data
    assert "revenue_estimate" in data
    assert "viability_analysis" in data
    assert data["success"] == True
    
    print("✅ Análisis con país específico exitoso")
    
    # Test 5: Validación de país requerido
    print("❌ Probando validación de país requerido...")
    
    invalid_data = {
        "city": "Berlin",
        "city_group": "Big Cities",
        "type": "FC",
        "open_date": "2023-01-15",
        "investment": 500000,
        "monthly_costs": 25000
    }
    
    response = client.post("/api/analyze", json=invalid_data)
    assert response.status_code == 400  # Debe fallar sin país
    
    print("✅ Validación de país requerido exitosa")
    
    # Test 6: Validación de país válido
    print("✅ Probando validación de país válido...")
    
    invalid_country_data = {
        "country": "InvalidCountry",
        "city": "Berlin",
        "city_group": "Big Cities",
        "type": "FC",
        "open_date": "2023-01-15",
        "investment": 500000,
        "monthly_costs": 25000
    }
    
    response = client.post("/api/analyze", json=invalid_country_data)
    assert response.status_code == 400  # Debe fallar con país inválido
    
    print("✅ Validación de país válido exitosa")
    
    print("\n" + "=" * 60)
    print("🎉 ¡TODOS LOS TESTS DEL SISTEMA DE PAÍSES PASARON!")
    print("✅ El sistema de países específicos está funcionando correctamente")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_country_system()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error en los tests del sistema de países: {e}")
        exit(1) 