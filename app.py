from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import pandas as pd
import numpy as np
import pickle
import os
import re
from dotenv import load_dotenv
import openai
from typing import Dict, Any, Optional
import json
from pydantic import BaseModel, validator
import logging
from datetime import datetime, timezone

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Modelos Pydantic para validación de datos
class RestaurantData(BaseModel):
    city: str
    city_group: str
    type: str
    open_date: str
    investment: float
    monthly_costs: float
    
    @validator('city')
    def validate_city(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Ciudad es requerida')
        if len(v) > 100:
            raise ValueError('Nombre de ciudad demasiado largo')
        # Sanitizar entrada
        v = re.sub(r'[<>"\']', '', v.strip())
        return v
    
    @validator('city_group')
    def validate_city_group(cls, v):
        allowed = ['Big Cities', 'Other']
        if v not in allowed:
            raise ValueError(f'city_group debe ser uno de: {allowed}')
        return v
    
    @validator('type')
    def validate_type(cls, v):
        allowed = ['FC', 'IL']
        if v not in allowed:
            raise ValueError(f'type debe ser uno de: {allowed}')
        return v
    
    @validator('investment', 'monthly_costs')
    def validate_amounts(cls, v):
        if v < 0:
            raise ValueError('Los montos no pueden ser negativos')
        if v > 10000000:  # 10 millones máximo
            raise ValueError('Monto demasiado alto')
        return v

class AIAdviceRequest(BaseModel):
    city: str
    type: str
    investment: float
    monthly_costs: float
    
    @validator('city')
    def validate_city(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Ciudad es requerida')
        v = re.sub(r'[<>"\']', '', v.strip())
        return v

# Configuración de la aplicación
app = FastAPI(
    title="Restaurant Advisor MVP", 
    version="1.0.0",
    description="MVP para análisis de viabilidad de restaurantes con IA"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de Supabase (opcional)
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = None

if supabase_url and supabase_key and supabase_url != "your_supabase_url":
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("✅ Supabase configurado correctamente")
    except Exception as e:
        logger.warning(f"⚠️ Error configurando Supabase: {e}")
        logger.info("El MVP funcionará sin almacenamiento en base de datos")
else:
    logger.warning("⚠️ Supabase no configurado - El MVP funcionará sin almacenamiento")

# Configuración de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuración de templates
templates = Jinja2Templates(directory="templates")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Rate limiting simple
from collections import defaultdict
import time
request_counts = defaultdict(list)

def check_rate_limit(client_ip: str, limit: int = 10, window: int = 60):
    """Rate limiting básico"""
    now = time.time()
    # Limpiar requests antiguos
    request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] 
                                if now - req_time < window]
    
    if len(request_counts[client_ip]) >= limit:
        raise HTTPException(status_code=429, detail="Demasiadas solicitudes")
    
    request_counts[client_ip].append(now)

def get_client_ip(request: Request) -> str:
    """Obtener IP del cliente de forma segura"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitizar entrada de datos"""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Remover caracteres peligrosos
            sanitized[key] = re.sub(r'[<>"\']', '', value.strip())
        else:
            sanitized[key] = value
    return sanitized

def validate_and_sanitize_restaurant_data(data: Dict[str, Any]) -> RestaurantData:
    """Validar y sanitizar datos del restaurante"""
    try:
        # Sanitizar entrada
        sanitized_data = sanitize_input(data)
        
        # Validar con Pydantic
        restaurant_data = RestaurantData(**sanitized_data)
        return restaurant_data
    except Exception as e:
        logger.error(f"Error validando datos: {e}")
        raise HTTPException(status_code=400, detail=f"Error en datos de entrada: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página principal"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/analyze")
async def analyze_restaurant(request: Request, data: Dict[str, Any]):
    """Analizar viabilidad de un restaurante con validación de seguridad"""
    
    # Rate limiting
    client_ip = get_client_ip(request)
    check_rate_limit(client_ip)
    
    try:
        # Validar y sanitizar datos
        restaurant_data = validate_and_sanitize_restaurant_data(data)
        
        # Análisis básico con validaciones adicionales
        investment = restaurant_data.investment
        monthly_costs = restaurant_data.monthly_costs
        
        # Validaciones de negocio
        if investment <= 0:
            raise HTTPException(status_code=400, detail="Inversión debe ser mayor a 0")
        
        if monthly_costs <= 0:
            raise HTTPException(status_code=400, detail="Costos mensuales deben ser mayores a 0")
        
        # Estimación de ingresos (simplificada pero segura)
        revenue_estimate = investment * 0.3  # 30% del capital inicial
        
        # Análisis de viabilidad
        annual_revenue = revenue_estimate
        annual_costs = monthly_costs * 12
        annual_profit = annual_revenue - annual_costs
        roi = (annual_profit / investment) * 100 if investment > 0 else 0
        
        viability_analysis = {
            "viability": "Alta" if annual_profit > 0 else "Baja",
            "annual_revenue": annual_revenue,
            "annual_profit": annual_profit,
            "roi": roi,
            "analysis_date": datetime.now(timezone.utc).isoformat()
        }
        
        # Guardar en Supabase si está configurado (con manejo de errores)
        if supabase:
            try:
                supabase.table("restaurant_analyses").insert({
                    "restaurant_data": restaurant_data.dict(),
                    "revenue_estimate": revenue_estimate,
                    "viability_analysis": viability_analysis
                }).execute()
                logger.info(f"Análisis guardado en Supabase para IP: {client_ip}")
            except Exception as e:
                logger.error(f"Error guardando en Supabase: {e}")
                # No fallar la aplicación si Supabase falla
        
        # Log de actividad
        logger.info(f"Análisis realizado para {restaurant_data.city} por IP: {client_ip}")
        
        return {
            "success": True,
            "revenue_estimate": revenue_estimate,
            "viability_analysis": viability_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en análisis: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/ai_advice")
async def get_ai_advice(request: Request, data: Dict[str, Any]):
    """Obtener consejos personalizados de IA con validación de seguridad"""
    
    # Rate limiting más estricto para IA
    client_ip = get_client_ip(request)
    check_rate_limit(client_ip, limit=5, window=60)  # 5 requests por minuto
    
    try:
        # Validar datos para consejos de IA
        if not openai.api_key or openai.api_key == "your_openai_api_key":
            return {
                "success": True,
                "advice": "Para recibir consejos personalizados de IA, configura tu API key de OpenAI en el archivo .env"
            }
        
        # Validar entrada
        advice_request = AIAdviceRequest(**sanitize_input(data))
        
        # Crear prompt seguro
        safe_prompt = f"""
        Analiza este proyecto de restaurante de manera profesional y constructiva:
        
        Ciudad: {advice_request.city}
        Tipo: {advice_request.type}
        Inversión: €{advice_request.investment:,.0f}
        Costos mensuales: €{advice_request.monthly_costs:,.0f}
        
        Proporciona:
        1. 3 recomendaciones específicas para mejorar la viabilidad
        2. Estrategias de marketing para la ubicación
        3. Consideraciones de costos y optimización
        4. Riesgos principales a considerar
        
        Responde en español de manera profesional y práctica.
        """
        
        # Llamada a OpenAI con timeout y manejo de errores
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto consultor de restaurantes con 20 años de experiencia."},
                    {"role": "user", "content": safe_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            advice = response.choices[0].message.content
            
            # Sanitizar respuesta de IA
            advice = re.sub(r'<[^>]*>', '', advice)  # Remover HTML tags
            advice = advice[:2000]  # Limitar longitud
            
        except Exception as e:
            logger.error(f"Error llamando a OpenAI: {e}")
            raise HTTPException(status_code=500, detail="Error al generar consejos de IA")
        
        # Guardar en Supabase si está configurado
        if supabase:
            try:
                supabase.table("ai_advice").insert({
                    "restaurant_data": advice_request.dict(),
                    "advice": advice
                }).execute()
                logger.info(f"Consejo de IA guardado para IP: {client_ip}")
            except Exception as e:
                logger.error(f"Error guardando consejo en Supabase: {e}")
        
        # Log de actividad
        logger.info(f"Consejo de IA generado para {advice_request.city} por IP: {client_ip}")
        
        return {"success": True, "advice": advice}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en consejos de IA: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/health")
async def health_check():
    """Endpoint de salud para monitoreo"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "openai": bool(openai.api_key and openai.api_key != "your_openai_api_key"),
            "supabase": bool(supabase)
        }
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejo personalizado de errores HTTP"""
    logger.warning(f"HTTP Error {exc.status_code}: {exc.detail} from IP: {get_client_ip(request)}")
    return {"error": exc.detail, "status_code": exc.status_code}

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejo de errores generales"""
    logger.error(f"Unexpected error: {exc} from IP: {get_client_ip(request)}")
    return {"error": "Error interno del servidor", "status_code": 500}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 