#!/usr/bin/env python3
"""
Script de prueba para las proyecciones financieras
"""

from investment_projection import investment_projection
import json

def test_projection():
    print("🚀 Probando sistema de proyecciones...")
    
    # Datos de ejemplo
    investment = 50000
    initial_revenue = 16301  # Del análisis anterior
    monthly_costs = 8000
    
    print(f"💰 Datos iniciales:")
    print(f"   Inversión: ${investment:,}")
    print(f"   Revenue inicial: ${initial_revenue:,}")
    print(f"   Costos mensuales: ${monthly_costs:,}")
    
    # Calcular proyección
    projection = investment_projection.calculate_projection(
        initial_investment=investment,
        initial_revenue=initial_revenue,
        initial_monthly_costs=monthly_costs,
        years=10
    )
    
    # Obtener métricas clave
    metrics = investment_projection.get_key_metrics(projection)
    
    print("\n📊 Proyecciones a 2, 5 y 10 años:")
    print("=" * 50)
    
    # Año 2
    year_2 = metrics["year_2"]
    print(f"📈 Año 2:")
    print(f"   Revenue: ${year_2['revenue']:,.2f}")
    print(f"   Profit: ${year_2['profit']:,.2f}")
    print(f"   ROI acumulado: {year_2['roi']:.1f}%")
    print(f"   Viabilidad: {year_2['viability']}")
    
    # Año 5
    year_5 = metrics["year_5"]
    print(f"\n📈 Año 5:")
    print(f"   Revenue: ${year_5['revenue']:,.2f}")
    print(f"   Profit: ${year_5['profit']:,.2f}")
    print(f"   ROI acumulado: {year_5['roi']:.1f}%")
    print(f"   Viabilidad: {year_5['viability']}")
    
    # Año 10
    year_10 = metrics["year_10"]
    print(f"\n📈 Año 10:")
    print(f"   Revenue: ${year_10['revenue']:,.2f}")
    print(f"   Profit: ${year_10['profit']:,.2f}")
    print(f"   ROI acumulado: {year_10['roi']:.1f}%")
    print(f"   Viabilidad: {year_10['viability']}")
    
    # Resumen
    summary = metrics["summary"]
    print(f"\n📋 Resumen 10 años:")
    print(f"   Profit total: ${summary['total_profit_10_years']:,.2f}")
    print(f"   ROI promedio anual: {summary['average_annual_roi']:.1f}%")
    print(f"   Viabilidad general: {summary['overall_viability']}")
    
    if summary['payback_period']['payback_year']:
        print(f"   Recuperación inversión: Año {summary['payback_period']['payback_year']}, Mes {summary['payback_period']['payback_month']}")
    else:
        print(f"   Recuperación inversión: No alcanzada en 10 años")
    
    if summary['break_even_year']:
        print(f"   Punto de equilibrio: Año {summary['break_even_year']}")
    else:
        print(f"   Punto de equilibrio: No alcanzado en 10 años")

if __name__ == "__main__":
    test_projection() 