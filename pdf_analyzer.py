import openai
import json
import logging
import time
from typing import Dict, Any, List, Optional
import re
from pathlib import Path
import os
from datetime import datetime

# Importar el sistema de caché
from pdf_cache_manager import pdf_cache, PDFAnalysis

logger = logging.getLogger(__name__)

class PDFAnalyzer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-3.5-turbo"  # Versión más económica
        self.max_tokens = 1000  # Limitar tokens para economía
    
    def analyze_pdf_content(self, text_content: str, pdf_context: str = "") -> Dict[str, Any]:
        """Analiza el contenido del PDF usando ChatGPT económico"""
        try:
            # Prompt optimizado para economía
            prompt = f"""
            Analiza este contenido de PDF relacionado con restaurantes y extrae información relevante:

            CONTENIDO: {text_content[:2000]}  # Limitar a 2000 caracteres

            Extrae y organiza la siguiente información en formato JSON:
            1. Datos demográficos (población, ingresos, edad)
            2. Información de competencia (restaurantes cercanos, precios)
            3. Indicadores económicos (PIB, desempleo, inflación)
            4. Eventos locales o estacionales
            5. Regulaciones o requisitos sanitarios
            6. Oportunidades de negocio identificadas
            7. Riesgos o amenazas detectadas

            Responde SOLO con JSON válido, sin texto adicional.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un analista experto en restaurantes. Extrae información relevante de PDFs y responde solo con JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            # Parsear respuesta JSON
            try:
                analysis = json.loads(response.choices[0].message.content)
                return {
                    "success": True,
                    "analysis": analysis,
                    "tokens_used": response.usage.total_tokens
                }
            except json.JSONDecodeError:
                # Si no es JSON válido, crear estructura básica
                return {
                    "success": True,
                    "analysis": {
                        "datos_demograficos": {},
                        "competencia": {},
                        "indicadores_economicos": {},
                        "eventos_locales": [],
                        "regulaciones": [],
                        "oportunidades": [],
                        "riesgos": []
                    },
                    "raw_response": response.choices[0].message.content,
                    "tokens_used": response.usage.total_tokens
                }
                
        except Exception as e:
            logger.error(f"Error en análisis de PDF: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": {}
            }
    
    def analyze_pdf_with_cache(self, file_path: str, file_id: str, filename: str) -> Dict[str, Any]:
        """Analiza PDF con sistema de caché inteligente"""
        start_time = time.time()
        
        try:
            # Verificar si ya existe análisis en caché
            cached_analysis = pdf_cache.get_cached_analysis(file_path)
            if cached_analysis:
                logger.info(f"✅ Usando análisis en caché para {filename}")
                return {
                    "success": True,
                    "analysis": cached_analysis.analysis_data,
                    "tokens_used": cached_analysis.tokens_used,
                    "processing_time": cached_analysis.processing_time,
                    "from_cache": True,
                    "cache_hit": True
                }
            
            # Si no está en caché, analizar el PDF
            logger.info(f"🔄 Analizando PDF nuevo: {filename}")
            
            # Extraer texto del PDF
            text_content = self._extract_text_from_file(file_path)
            if not text_content:
                raise Exception("No se pudo extraer texto del PDF")
            
            # Analizar contenido
            analysis_result = self.analyze_pdf_content(text_content)
            
            processing_time = time.time() - start_time
            
            if analysis_result["success"]:
                # Crear objeto de análisis para caché
                analysis_obj = PDFAnalysis(
                    file_id=file_id,
                    filename=filename,
                    file_hash=pdf_cache._calculate_file_hash(file_path),
                    analysis_date=datetime.now().isoformat(),
                    analysis_data=analysis_result["analysis"],
                    tokens_used=analysis_result.get("tokens_used", 0),
                    processing_time=processing_time,
                    status="completed"
                )
                
                # Guardar en caché
                pdf_cache.save_analysis(analysis_obj)
                
                logger.info(f"✅ Análisis completado y guardado en caché: {filename}")
                
                return {
                    "success": True,
                    "analysis": analysis_result["analysis"],
                    "tokens_used": analysis_result.get("tokens_used", 0),
                    "processing_time": processing_time,
                    "from_cache": False,
                    "cache_hit": False
                }
            else:
                # Guardar análisis fallido en caché
                analysis_obj = PDFAnalysis(
                    file_id=file_id,
                    filename=filename,
                    file_hash=pdf_cache._calculate_file_hash(file_path),
                    analysis_date=datetime.now().isoformat(),
                    analysis_data={},
                    tokens_used=0,
                    processing_time=processing_time,
                    status="failed",
                    error_message=analysis_result.get("error", "Error desconocido")
                )
                
                pdf_cache.save_analysis(analysis_obj)
                
                return analysis_result
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error analizando PDF con caché: {e}")
            
            # Guardar error en caché
            analysis_obj = PDFAnalysis(
                file_id=file_id,
                filename=filename,
                file_hash=pdf_cache._calculate_file_hash(file_path),
                analysis_date=datetime.now().isoformat(),
                analysis_data={},
                tokens_used=0,
                processing_time=processing_time,
                status="failed",
                error_message=str(e)
            )
            
            pdf_cache.save_analysis(analysis_obj)
            
            return {
                "success": False,
                "error": str(e),
                "analysis": {},
                "processing_time": processing_time,
                "from_cache": False,
                "cache_hit": False
            }
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """Extrae texto del archivo PDF"""
        try:
            import PyPDF2
            import pdfplumber
            
            text = ""
            
            # Método 1: PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            # Si no hay texto, intentar con pdfplumber
            if not text.strip():
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extrayendo texto del PDF: {e}")
            return ""
    
    def extract_restaurant_data(self, text_content: str) -> Dict[str, Any]:
        """Extrae datos específicos de restaurantes del PDF"""
        try:
            prompt = f"""
            Extrae datos específicos de restaurantes de este texto:

            TEXTO: {text_content[:1500]}

            Busca y extrae:
            - Nombres de restaurantes
            - Direcciones y ubicaciones
            - Precios y costos
            - Horarios de operación
            - Información de contacto
            - Reseñas y calificaciones

            Responde en JSON con esta estructura:
            {{
                "restaurantes": [
                    {{
                        "nombre": "",
                        "direccion": "",
                        "precio_promedio": "",
                        "horarios": "",
                        "contacto": "",
                        "calificacion": ""
                    }}
                ]
            }}
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extrae datos específicos de restaurantes. Responde solo con JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2
            )
            
            try:
                data = json.loads(response.choices[0].message.content)
                return {
                    "success": True,
                    "data": data,
                    "tokens_used": response.usage.total_tokens
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "data": {"restaurantes": []},
                    "raw_response": response.choices[0].message.content,
                    "tokens_used": response.usage.total_tokens
                }
                
        except Exception as e:
            logger.error(f"Error al extraer datos de restaurantes: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {"restaurantes": []}
            }
    
    def generate_insights(self, pdf_analysis: Dict[str, Any], restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera insights basados en el análisis del PDF"""
        try:
            # Combinar análisis y datos
            combined_data = {
                "analisis_pdf": pdf_analysis,
                "datos_restaurantes": restaurant_data
            }
            
            prompt = f"""
            Basado en este análisis de PDF, genera insights para un restaurante:

            DATOS: {json.dumps(combined_data, ensure_ascii=False)[:1000]}

            Genera insights en estas categorías:
            1. Oportunidades de mercado
            2. Amenazas competitivas
            3. Recomendaciones estratégicas
            4. Factores de riesgo
            5. Ventajas competitivas

            Responde en JSON con esta estructura:
            {{
                "oportunidades": [],
                "amenazas": [],
                "recomendaciones": [],
                "riesgos": [],
                "ventajas": []
            }}
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Genera insights estratégicos para restaurantes. Responde solo con JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.4
            )
            
            try:
                insights = json.loads(response.choices[0].message.content)
                return {
                    "success": True,
                    "insights": insights,
                    "tokens_used": response.usage.total_tokens
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "insights": {
                        "oportunidades": [],
                        "amenazas": [],
                        "recomendaciones": [],
                        "riesgos": [],
                        "ventajas": []
                    },
                    "raw_response": response.choices[0].message.content,
                    "tokens_used": response.usage.total_tokens
                }
                
        except Exception as e:
            logger.error(f"Error al generar insights: {e}")
            return {
                "success": False,
                "error": str(e),
                "insights": {}
            }
    
    def get_cost_estimate(self, text_length: int) -> Dict[str, Any]:
        """Estima el costo del análisis basado en la longitud del texto"""
        # Estimación aproximada de tokens
        estimated_tokens = text_length * 1.5  # Factor de conversión
        estimated_cost = (estimated_tokens / 1000) * 0.002  # Costo por 1K tokens en gpt-3.5-turbo
        
        return {
            "estimated_tokens": int(estimated_tokens),
            "estimated_cost_usd": round(estimated_cost, 4),
            "model_used": self.model
        }

# Instancia global
pdf_analyzer = PDFAnalyzer() 