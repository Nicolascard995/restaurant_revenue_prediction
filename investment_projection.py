#!/usr/bin/env python3
"""
Sistema de proyecciones financieras para restaurantes
Proyecciones a 2, 5 y 10 años con análisis de viabilidad
"""

import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class InvestmentProjection:
    def __init__(self):
        self.growth_rates = {
            "revenue": {
                "year_1": 0.15,    # 15% crecimiento año 1
                "year_2": 0.12,    # 12% crecimiento año 2
                "year_3_5": 0.08,  # 8% crecimiento años 3-5
                "year_6_10": 0.05  # 5% crecimiento años 6-10
            },
            "costs": {
                "year_1": 0.08,    # 8% incremento costos año 1
                "year_2": 0.06,    # 6% incremento costos año 2
                "year_3_5": 0.04,  # 4% incremento costos años 3-5
                "year_6_10": 0.03  # 3% incremento costos años 6-10
            }
        }
    
    def calculate_projection(self, 
                           initial_investment: float,
                           initial_revenue: float,
                           initial_monthly_costs: float,
                           years: int = 10) -> Dict[str, Any]:
        """
        Calcula proyección financiera a largo plazo
        """
        try:
            projection = {
                "initial_data": {
                    "investment": initial_investment,
                    "initial_revenue": initial_revenue,
                    "initial_monthly_costs": initial_monthly_costs,
                    "initial_annual_costs": initial_monthly_costs * 12
                },
                "projection_years": years,
                "yearly_data": [],
                "summary": {}
            }
            
            current_revenue = initial_revenue
            current_monthly_costs = initial_monthly_costs
            
            total_profit = 0
            total_revenue = 0
            total_costs = 0
            
            for year in range(1, years + 1):
                # Calcular crecimiento de revenue
                if year == 1:
                    revenue_growth = self.growth_rates["revenue"]["year_1"]
                elif year == 2:
                    revenue_growth = self.growth_rates["revenue"]["year_2"]
                elif year <= 5:
                    revenue_growth = self.growth_rates["revenue"]["year_3_5"]
                else:
                    revenue_growth = self.growth_rates["revenue"]["year_6_10"]
                
                # Calcular incremento de costos
                if year == 1:
                    cost_growth = self.growth_rates["costs"]["year_1"]
                elif year == 2:
                    cost_growth = self.growth_rates["costs"]["year_2"]
                elif year <= 5:
                    cost_growth = self.growth_rates["costs"]["year_3_5"]
                else:
                    cost_growth = self.growth_rates["costs"]["year_6_10"]
                
                # Aplicar crecimientos
                current_revenue *= (1 + revenue_growth)
                current_monthly_costs *= (1 + cost_growth)
                current_annual_costs = current_monthly_costs * 12
                
                # Calcular métricas del año
                annual_profit = current_revenue - current_annual_costs
                cumulative_profit = total_profit + annual_profit
                roi_annual = (annual_profit / initial_investment) * 100
                roi_cumulative = (cumulative_profit / initial_investment) * 100
                
                # Determinar viabilidad
                viability = "High" if annual_profit > 0 else "Low"
                if annual_profit > initial_investment * 0.2:  # 20% del ROI
                    viability = "Excellent"
                elif annual_profit > 0:
                    viability = "Medium"
                
                year_data = {
                    "year": year,
                    "revenue": round(current_revenue, 2),
                    "monthly_costs": round(current_monthly_costs, 2),
                    "annual_costs": round(current_annual_costs, 2),
                    "annual_profit": round(annual_profit, 2),
                    "cumulative_profit": round(cumulative_profit, 2),
                    "roi_annual": round(roi_annual, 2),
                    "roi_cumulative": round(roi_cumulative, 2),
                    "viability": viability,
                    "revenue_growth_rate": revenue_growth,
                    "cost_growth_rate": cost_growth
                }
                
                projection["yearly_data"].append(year_data)
                
                # Acumular totales
                total_profit += annual_profit
                total_revenue += current_revenue
                total_costs += current_annual_costs
            
            # Calcular resumen
            projection["summary"] = {
                "total_profit_10_years": round(total_profit, 2),
                "total_revenue_10_years": round(total_revenue, 2),
                "total_costs_10_years": round(total_costs, 2),
                "average_annual_profit": round(total_profit / years, 2),
                "average_annual_roi": round((total_profit / years / initial_investment) * 100, 2),
                "total_roi_10_years": round((total_profit / initial_investment) * 100, 2),
                "payback_period": self._calculate_payback_period(projection["yearly_data"], initial_investment),
                "break_even_year": self._calculate_break_even_year(projection["yearly_data"]),
                "overall_viability": self._determine_overall_viability(projection["yearly_data"])
            }
            
            return projection
            
        except Exception as e:
            logger.error(f"Error en cálculo de proyección: {e}")
            return {"error": str(e)}
    
    def _calculate_payback_period(self, yearly_data: List[Dict], initial_investment: float) -> Dict[str, Any]:
        """Calcula el período de recuperación de la inversión"""
        cumulative_profit = 0
        payback_year = None
        payback_month = None
        
        for year_data in yearly_data:
            cumulative_profit += year_data["annual_profit"]
            if cumulative_profit >= initial_investment and payback_year is None:
                payback_year = year_data["year"]
                # Calcular mes aproximado
                remaining_to_payback = initial_investment - (cumulative_profit - year_data["annual_profit"])
                payback_month = int((remaining_to_payback / year_data["annual_profit"]) * 12)
                break
        
        return {
            "payback_year": payback_year,
            "payback_month": payback_month,
            "payback_period_months": (payback_year * 12 + payback_month) if payback_year else None
        }
    
    def _calculate_break_even_year(self, yearly_data: List[Dict]) -> int:
        """Calcula el año en que se alcanza el punto de equilibrio"""
        for year_data in yearly_data:
            if year_data["annual_profit"] > 0:
                return year_data["year"]
        return None
    
    def _determine_overall_viability(self, yearly_data: List[Dict]) -> str:
        """Determina la viabilidad general del proyecto"""
        profitable_years = sum(1 for year in yearly_data if year["annual_profit"] > 0)
        total_years = len(yearly_data)
        
        if profitable_years >= total_years * 0.8:  # 80% de años rentables
            return "Excellent"
        elif profitable_years >= total_years * 0.6:  # 60% de años rentables
            return "High"
        elif profitable_years >= total_years * 0.4:  # 40% de años rentables
            return "Medium"
        else:
            return "Low"
    
    def get_key_metrics(self, projection: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae métricas clave de la proyección"""
        if "error" in projection:
            return projection
        
        summary = projection["summary"]
        yearly_data = projection["yearly_data"]
        
        # Métricas a 2, 5 y 10 años
        metrics = {
            "year_2": {
                "revenue": yearly_data[1]["revenue"] if len(yearly_data) > 1 else 0,
                "profit": yearly_data[1]["annual_profit"] if len(yearly_data) > 1 else 0,
                "roi": yearly_data[1]["roi_cumulative"] if len(yearly_data) > 1 else 0,
                "viability": yearly_data[1]["viability"] if len(yearly_data) > 1 else "Low"
            },
            "year_5": {
                "revenue": yearly_data[4]["revenue"] if len(yearly_data) > 4 else 0,
                "profit": yearly_data[4]["annual_profit"] if len(yearly_data) > 4 else 0,
                "roi": yearly_data[4]["roi_cumulative"] if len(yearly_data) > 4 else 0,
                "viability": yearly_data[4]["viability"] if len(yearly_data) > 4 else "Low"
            },
            "year_10": {
                "revenue": yearly_data[9]["revenue"] if len(yearly_data) > 9 else 0,
                "profit": yearly_data[9]["annual_profit"] if len(yearly_data) > 9 else 0,
                "roi": yearly_data[9]["roi_cumulative"] if len(yearly_data) > 9 else 0,
                "viability": yearly_data[9]["viability"] if len(yearly_data) > 9 else "Low"
            },
            "summary": {
                "total_profit_10_years": summary["total_profit_10_years"],
                "average_annual_roi": summary["average_annual_roi"],
                "payback_period": summary["payback_period"],
                "break_even_year": summary["break_even_year"],
                "overall_viability": summary["overall_viability"]
            }
        }
        
        return metrics

# Instancia global
investment_projection = InvestmentProjection() 