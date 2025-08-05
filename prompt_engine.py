import openai
import json
import logging
from typing import Dict, Any, List
import os

logger = logging.getLogger(__name__)

class PromptEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        self.model = "gpt-3.5-turbo"  # Versión más económica
        self.max_tokens = 800  # Limitar tokens para economía
    
    def create_context_prompt(self, restaurant_data: Dict[str, Any], pdf_data: Dict[str, Any] = None) -> str:
        """Crea un prompt contextual optimizado para economía"""
        
        # Construir contexto básico
        context = f"""
        RESTAURANTE: {restaurant_data.get('city', 'N/A')} - {restaurant_data.get('type', 'N/A')}
        INVERSIÓN: ${restaurant_data.get('investment', 0):,.2f}
        COSTOS MENSUALES: ${restaurant_data.get('monthly_costs', 0):,.2f}
        """
        
        # Agregar datos de PDF si están disponibles
        if pdf_data and pdf_data.get('analysis'):
            pdf_analysis = pdf_data['analysis']
            context += f"""
        DATOS DE PDF:
        - Demografía: {pdf_analysis.get('datos_demograficos', {})}
        - Competencia: {pdf_analysis.get('competencia', {})}
        - Economía: {pdf_analysis.get('indicadores_economicos', {})}
        """
        
        return context
    
    def analyze_viability(self, restaurant_data: Dict[str, Any], pdf_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analiza viabilidad usando prompt económico"""
        try:
            context = self.create_context_prompt(restaurant_data, pdf_data)
            
            prompt = f"""
            {context}
            
            Analiza la viabilidad de este restaurante. Responde en JSON:
            {{
                "viabilidad_score": 1-10,
                "factores_positivos": [],
                "factores_negativos": [],
                "recomendaciones": [],
                "riesgo_nivel": "bajo/medio/alto"
            }}
            """

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Analiza viabilidad de restaurantes. Responde solo con JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            try:
                analysis = json.loads(response.choices[0].message.content)
                return {
                    "success": True,
                    "analysis": analysis,
                    "tokens_used": response.usage.total_tokens
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "analysis": {
                        "viabilidad_score": 5,
                        "factores_positivos": [],
                        "factores_negativos": [],
                        "recomendaciones": [],
                        "riesgo_nivel": "medio"
                    },
                    "tokens_used": response.usage.total_tokens
                }
                
        except Exception as e:
            logger.error(f"Error en análisis de viabilidad: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": {}
            }
    
    def predict_revenue(self, restaurant_data: Dict[str, Any], pdf_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Predice revenue usando prompt económico"""
        try:
            context = self.create_context_prompt(restaurant_data, pdf_data)
            
            prompt = f"""
            {context}
            
            Predice el revenue mensual. Responde en JSON:
            {{
                "revenue_prediccion": 0,
                "rango_min": 0,
                "rango_max": 0,
                "factores_clave": [],
                "confianza": "alta/media/baja"
            }}
            """

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Predice revenue de restaurantes. Responde solo con JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.2
            )
            
            try:
                prediction = json.loads(response.choices[0].message.content)
                return {
                    "success": True,
                    "prediction": prediction,
                    "tokens_used": response.usage.total_tokens
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "prediction": {
                        "revenue_prediccion": 0,
                        "rango_min": 0,
                        "rango_max": 0,
                        "factores_clave": [],
                        "confianza": "media"
                    },
                    "tokens_used": response.usage.total_tokens
                }
                
        except Exception as e:
            logger.error(f"Error en predicción de revenue: {e}")
            return {
                "success": False,
                "error": str(e),
                "prediction": {}
            }
    
    def analyze_competition(self, location: str, pdf_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analiza competencia usando prompt económico"""
        try:
            context = f"UBICACIÓN: {location}"
            if pdf_data and pdf_data.get('analysis'):
                context += f"\nDATOS PDF: {pdf_data['analysis'].get('competencia', {})}"
            
            prompt = f"""
            {context}
            
            Analiza la competencia. Responde en JSON:
            {{
                "nivel_competencia": "bajo/medio/alto",
                "amenazas": [],
                "oportunidades": [],
                "recomendaciones": []
            }}
            """

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Analiza competencia de restaurantes. Responde solo con JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            try:
                analysis = json.loads(response.choices[0].message.content)
                return {
                    "success": True,
                    "analysis": analysis,
                    "tokens_used": response.usage.total_tokens
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "analysis": {
                        "nivel_competencia": "medio",
                        "amenazas": [],
                        "oportunidades": [],
                        "recomendaciones": []
                    },
                    "tokens_used": response.usage.total_tokens
                }
                
        except Exception as e:
            logger.error(f"Error en análisis de competencia: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": {}
            }
    
    def generate_strategic_recommendations(self, restaurant_data: Dict[str, Any], pdf_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Genera recomendaciones estratégicas usando prompt económico"""
        try:
            context = self.create_context_prompt(restaurant_data, pdf_data)
            
            prompt = f"""
            {context}
            
            Genera recomendaciones estratégicas. Responde en JSON:
            {{
                "recomendaciones_corto_plazo": [],
                "recomendaciones_largo_plazo": [],
                "prioridades": [],
                "acciones_inmediatas": []
            }}
            """

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Genera recomendaciones estratégicas. Responde solo con JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.4
            )
            
            try:
                recommendations = json.loads(response.choices[0].message.content)
                return {
                    "success": True,
                    "recommendations": recommendations,
                    "tokens_used": response.usage.total_tokens
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "recommendations": {
                        "recomendaciones_corto_plazo": [],
                        "recomendaciones_largo_plazo": [],
                        "prioridades": [],
                        "acciones_inmediatas": []
                    },
                    "tokens_used": response.usage.total_tokens
                }
                
        except Exception as e:
            logger.error(f"Error en recomendaciones estratégicas: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": {}
            }
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de costos de tokens"""
        return {
            "model": self.model,
            "max_tokens_per_request": self.max_tokens,
            "estimated_cost_per_request": round((self.max_tokens / 1000) * 0.002, 4),
            "cost_optimization": "Usando gpt-3.5-turbo y tokens limitados"
        }

# Instancia global
prompt_engine = PromptEngine() 