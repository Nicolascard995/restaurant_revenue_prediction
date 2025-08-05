#!/usr/bin/env python3
"""
Datos específicos por país para predicciones más precisas
Basado en el análisis del PDF de predicción multi-mercado
"""

from typing import Dict, Any, List

# Datos demográficos y económicos por país
COUNTRY_DATA = {
    "Germany": {
        "name": "Alemania",
        "currency": "EUR",
        "population": 83190556,
        "gdp_per_capita": 46468,
        "restaurant_market_size": 85000000000,  # 85 mil millones EUR
        "avg_restaurant_revenue": 450000,
        "avg_restaurant_profit_margin": 0.08,
        "major_cities": [
            "Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt",
            "Stuttgart", "Düsseldorf", "Dortmund", "Essen", "Leipzig"
        ],
        "restaurant_types": {
            "FC": {
                "avg_investment": 300000,
                "avg_monthly_costs": 25000,
                "avg_revenue": 400000,
                "success_rate": 0.75
            },
            "IL": {
                "avg_investment": 500000,
                "avg_monthly_costs": 35000,
                "avg_revenue": 600000,
                "success_rate": 0.65
            }
        },
        "economic_factors": {
            "inflation_rate": 0.03,
            "unemployment_rate": 0.05,
            "consumer_confidence": 0.7,
            "tourism_growth": 0.04
        },
        "regulations": [
            "Estrictas regulaciones sanitarias",
            "Certificaciones de calidad obligatorias",
            "Horarios de operación regulados",
            "Impuestos específicos para restaurantes"
        ]
    },
    
    "Argentina": {
        "name": "Argentina",
        "currency": "ARS",
        "population": 45195774,
        "gdp_per_capita": 8500,
        "restaurant_market_size": 15000000000,  # 15 mil millones USD
        "avg_restaurant_revenue": 180000,
        "avg_restaurant_profit_margin": 0.12,
        "major_cities": [
            "Buenos Aires", "Córdoba", "Rosario", "Mendoza", "La Plata",
            "Tucumán", "Salta", "Santa Fe", "San Juan", "Neuquén"
        ],
        "restaurant_types": {
            "FC": {
                "avg_investment": 80000,
                "avg_monthly_costs": 8000,
                "avg_revenue": 150000,
                "success_rate": 0.70
            },
            "IL": {
                "avg_investment": 150000,
                "avg_monthly_costs": 12000,
                "avg_revenue": 250000,
                "success_rate": 0.60
            }
        },
        "economic_factors": {
            "inflation_rate": 0.50,
            "unemployment_rate": 0.10,
            "consumer_confidence": 0.45,
            "tourism_growth": 0.08
        },
        "regulations": [
            "Regulaciones sanitarias moderadas",
            "Certificaciones de calidad recomendadas",
            "Horarios flexibles de operación",
            "Impuestos variables por región"
        ]
    },
    
    "Mexico": {
        "name": "México",
        "currency": "MXN",
        "population": 128932753,
        "gdp_per_capita": 9500,
        "restaurant_market_size": 25000000000,  # 25 mil millones USD
        "avg_restaurant_revenue": 200000,
        "avg_restaurant_profit_margin": 0.15,
        "major_cities": [
            "Mexico City", "Guadalajara", "Monterrey", "Puebla", "Tijuana",
            "León", "Juárez", "Zapopan", "Nezahualcóyotl", "Chihuahua"
        ],
        "restaurant_types": {
            "FC": {
                "avg_investment": 100000,
                "avg_monthly_costs": 10000,
                "avg_revenue": 180000,
                "success_rate": 0.72
            },
            "IL": {
                "avg_investment": 200000,
                "avg_monthly_costs": 15000,
                "avg_revenue": 300000,
                "success_rate": 0.62
            }
        },
        "economic_factors": {
            "inflation_rate": 0.06,
            "unemployment_rate": 0.04,
            "consumer_confidence": 0.65,
            "tourism_growth": 0.12
        },
        "regulations": [
            "Regulaciones sanitarias estándar",
            "Certificaciones de calidad requeridas",
            "Horarios de operación flexibles",
            "Impuestos federales y estatales"
        ]
    }
}

def get_country_data(country: str) -> Dict[str, Any]:
    """Obtiene datos específicos de un país"""
    return COUNTRY_DATA.get(country, {})

def get_cities_by_country(country: str) -> List[str]:
    """Obtiene lista de ciudades principales por país"""
    country_data = get_country_data(country)
    return country_data.get("major_cities", [])

def get_restaurant_type_data(country: str, restaurant_type: str) -> Dict[str, Any]:
    """Obtiene datos específicos por tipo de restaurante y país"""
    country_data = get_country_data(country)
    restaurant_types = country_data.get("restaurant_types", {})
    return restaurant_types.get(restaurant_type, {})

def calculate_country_adjusted_revenue(
    base_revenue: float,
    country: str,
    restaurant_type: str,
    city_group: str
) -> float:
    """Calcula revenue ajustado por país y tipo de restaurante"""
    country_data = get_country_data(country)
    type_data = get_restaurant_type_data(country, restaurant_type)
    
    if not country_data or not type_data:
        return base_revenue
    
    # Factores de ajuste por país
    country_multiplier = {
        "Germany": 1.0,      # Base
        "Argentina": 0.4,     # Mercado más pequeño
        "Mexico": 0.45        # Mercado mediano
    }
    
    # Factores por tipo de ciudad
    city_multiplier = {
        "Big Cities": 1.2,
        "Other": 0.8
    }
    
    # Factor de éxito por país
    success_rate = type_data.get("success_rate", 0.7)
    
    # Cálculo ajustado
    adjusted_revenue = (
        base_revenue *
        country_multiplier.get(country, 1.0) *
        city_multiplier.get(city_group, 1.0) *
        success_rate
    )
    
    return adjusted_revenue

def get_country_economic_insights(country: str) -> Dict[str, Any]:
    """Obtiene insights económicos específicos por país"""
    country_data = get_country_data(country)
    economic_factors = country_data.get("economic_factors", {})
    
    insights = {
        "country_name": country_data.get("name", country),
        "currency": country_data.get("currency", "USD"),
        "market_size": country_data.get("restaurant_market_size", 0),
        "avg_revenue": country_data.get("avg_restaurant_revenue", 0),
        "profit_margin": country_data.get("avg_restaurant_profit_margin", 0),
        "economic_indicators": economic_factors,
        "regulations": country_data.get("regulations", []),
        "opportunities": [],
        "risks": []
    }
    
    # Análisis de oportunidades y riesgos por país
    if country == "Germany":
        insights["opportunities"] = [
            "Mercado maduro y estable",
            "Alto poder adquisitivo",
            "Turismo internacional fuerte",
            "Regulaciones claras y consistentes"
        ]
        insights["risks"] = [
            "Alta competencia",
            "Costos operativos elevados",
            "Regulaciones estrictas",
            "Mercado saturado en grandes ciudades"
        ]
    
    elif country == "Argentina":
        insights["opportunities"] = [
            "Cultura gastronómica rica",
            "Costos operativos relativamente bajos",
            "Potencial de crecimiento",
            "Turismo gastronómico emergente"
        ]
        insights["risks"] = [
            "Inestabilidad económica",
            "Alta inflación",
            "Regulaciones cambiantes",
            "Volatilidad cambiaria"
        ]
    
    elif country == "Mexico":
        insights["opportunities"] = [
            "Mercado en crecimiento",
            "Cultura gastronómica diversa",
            "Turismo internacional fuerte",
            "Costos operativos moderados"
        ]
        insights["risks"] = [
            "Competencia local fuerte",
            "Regulaciones complejas",
            "Seguridad en algunas regiones",
            "Dependencia del turismo"
        ]
    
    return insights

def get_country_recommendations(country: str, restaurant_type: str, investment: float) -> List[str]:
    """Genera recomendaciones específicas por país"""
    country_data = get_country_data(country)
    type_data = get_restaurant_type_data(country, restaurant_type)
    
    recommendations = []
    
    # Recomendaciones por país
    if country == "Germany":
        recommendations.extend([
            "Enfócate en calidad y sostenibilidad",
            "Considera certificaciones orgánicas",
            "Desarrolla una propuesta gastronómica única",
            "Invierte en tecnología y eficiencia operativa"
        ])
    
    elif country == "Argentina":
        recommendations.extend([
            "Adapta tu menú a la cultura local",
            "Considera precios competitivos",
            "Desarrolla relaciones con proveedores locales",
            "Planifica para la inflación"
        ])
    
    elif country == "Mexico":
        recommendations.extend([
            "Incorpora sabores locales auténticos",
            "Considera múltiples ubicaciones",
            "Desarrolla una fuerte presencia digital",
            "Enfócate en la experiencia del cliente"
        ])
    
    # Recomendaciones por tipo de restaurante
    if restaurant_type == "FC":
        recommendations.extend([
            "Optimiza procesos para eficiencia",
            "Considera franquicias o expansión",
            "Enfócate en velocidad de servicio"
        ])
    else:  # IL
        recommendations.extend([
            "Desarrolla una propuesta gastronómica única",
            "Invierte en ambiente y experiencia",
            "Considera eventos y catering"
        ])
    
    return recommendations 