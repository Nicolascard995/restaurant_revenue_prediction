from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import numpy as np
import pickle
import os
import re
from dotenv import load_dotenv
import openai
from typing import Dict, Any, Optional, List
import json
from pydantic import BaseModel, validator
import logging
from datetime import datetime, timezone
import sys

# Importar módulos de PDF
from pdf_upload import pdf_manager
from pdf_analyzer import pdf_analyzer
from prompt_engine import prompt_engine

# Importar integración ML
from ml_model_integration import ml_integration

# Importar proyecciones financieras
from investment_projection import investment_projection

# Configure logging with detailed error tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables with error handling
try:
    load_dotenv()
    logger.info("✅ Environment variables loaded successfully")
except Exception as e:
    logger.error(f"❌ Error loading environment variables: {e}")

# Pydantic models for data validation
class RestaurantData(BaseModel):
    country: str
    city: str
    city_group: str
    type: str
    open_date: str
    investment: float
    monthly_costs: float
    language: str = "en"  # Default to English
    
    @validator('country')
    def validate_country(cls, v):
        allowed = ['Germany', 'Argentina', 'Mexico']
        if v not in allowed:
            raise ValueError(f'country must be one of: {allowed}')
        return v
    
    @validator('city')
    def validate_city(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('City is required')
        if len(v) > 100:
            raise ValueError('City name too long')
        # Sanitize input
        v = re.sub(r'[<>"\']', '', v.strip())
        return v
    
    @validator('city_group')
    def validate_city_group(cls, v):
        allowed = ['Big Cities', 'Other']
        if v not in allowed:
            raise ValueError(f'city_group must be one of: {allowed}')
        return v
    
    @validator('type')
    def validate_type(cls, v):
        allowed = ['FC', 'IL']
        if v not in allowed:
            raise ValueError(f'type must be one of: {allowed}')
        return v
    
    @validator('investment', 'monthly_costs')
    def validate_amounts(cls, v):
        if v < 0:
            raise ValueError('Amounts cannot be negative')
        if v > 10000000:  # 10 million maximum
            raise ValueError('Amount too high')
        return v
    
    @validator('language')
    def validate_language(cls, v):
        allowed = ['en', 'es', 'de']  # English, Spanish, German
        if v not in allowed:
            raise ValueError(f'language must be one of: {allowed}')
        return v

class AIAdviceRequest(BaseModel):
    city: str
    type: str
    investment: float
    monthly_costs: float
    
    @validator('city')
    def validate_city(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('City is required')
        v = re.sub(r'[<>"\']', '', v.strip())
        return v

# Application configuration with error handling
try:
    app = FastAPI(
        title="Restaurant Advisor MVP", 
        version="1.0.0",
        description="MVP for restaurant viability analysis with AI"
    )
    logger.info("✅ FastAPI application created successfully")
except Exception as e:
    logger.error(f"❌ Error creating FastAPI app: {e}")
    sys.exit(1)

# Configure CORS with error handling
try:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("✅ CORS middleware configured successfully")
except Exception as e:
    logger.error(f"❌ Error configuring CORS: {e}")

# Supabase configuration with comprehensive error handling
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = None

if supabase_url and supabase_key and supabase_url != "your_supabase_url":
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("✅ Supabase configured successfully")
    except ImportError as e:
        logger.warning(f"⚠️ Supabase library not available: {e}")
        logger.info("MVP will work without database storage")
    except Exception as e:
        logger.warning(f"⚠️ Error configuring Supabase: {e}")
        logger.info("MVP will work without database storage")
else:
    logger.warning("⚠️ Supabase not configured - MVP will work without storage")

# OpenAI configuration with error handling
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if openai.api_key:
        logger.info("✅ OpenAI configured successfully")
    else:
        logger.warning("⚠️ OpenAI API key not found")
except Exception as e:
    logger.error(f"❌ Error configuring OpenAI: {e}")

# Template configuration with error handling
try:
    templates = Jinja2Templates(directory="templates")
    logger.info("✅ Templates configured successfully")
except Exception as e:
    logger.error(f"❌ Error configuring templates: {e}")

# Mount static files with error handling
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("✅ Static files mounted successfully")
except Exception as e:
    logger.error(f"❌ Error mounting static files: {e}")

# Simple rate limiting with error handling
from collections import defaultdict
import time
request_counts = defaultdict(list)

def check_rate_limit(client_ip: str, limit: int = 10, window: int = 60):
    """Basic rate limiting with error handling"""
    try:
        now = time.time()
        # Clean old requests
        request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] 
                                    if now - req_time < window]
        
        if len(request_counts[client_ip]) >= limit:
            raise HTTPException(status_code=429, detail="Too many requests")
        
        request_counts[client_ip].append(now)
    except Exception as e:
        logger.error(f"❌ Rate limiting error: {e}")
        # Don't block requests if rate limiting fails

def get_client_ip(request: Request) -> str:
    """Get client IP safely with error handling"""
    try:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    except Exception as e:
        logger.error(f"❌ Error getting client IP: {e}")
        return "unknown"

def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize input data with error handling"""
    try:
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Remove dangerous characters
                sanitized[key] = re.sub(r'[<>"\']', '', value.strip())
            else:
                sanitized[key] = value
        return sanitized
    except Exception as e:
        logger.error(f"❌ Error sanitizing input: {e}")
        return data

def validate_and_sanitize_restaurant_data(data: Dict[str, Any]) -> RestaurantData:
    """Validate and sanitize restaurant data with comprehensive error handling"""
    try:
        # Sanitize input
        sanitized_data = sanitize_input(data)
        
        # Validate with Pydantic
        restaurant_data = RestaurantData(**sanitized_data)
        return restaurant_data
    except Exception as e:
        logger.error(f"❌ Error validating data: {e}")
        raise HTTPException(status_code=400, detail=f"Input data error: {str(e)}")

def simple_revenue_prediction(investment: float, monthly_costs: float, country: str, city_group: str, restaurant_type: str) -> float:
    """Revenue prediction adjusted by country and restaurant type"""
    try:
        from country_data import calculate_country_adjusted_revenue, get_restaurant_type_data
        
        # Get country-specific data
        type_data = get_restaurant_type_data(country, restaurant_type)
        
        if type_data:
            # Use country-specific data if available
            avg_revenue = type_data.get("avg_revenue", 0)
            success_rate = type_data.get("success_rate", 0.7)
            
            # Adjust by investment and costs
            investment_factor = investment / type_data.get("avg_investment", 100000)
            cost_factor = monthly_costs / type_data.get("avg_monthly_costs", 10000)
            
            # Adjusted calculation
            adjusted_revenue = avg_revenue * investment_factor * cost_factor * success_rate
        else:
            # Fallback to simple calculation
            base_revenue = investment * 0.3
            city_multiplier = 1.2 if city_group == "Big Cities" else 0.8
            type_multiplier = 1.1 if restaurant_type == "FC" else 0.9
            adjusted_revenue = base_revenue * city_multiplier * type_multiplier
        
        # Apply country-specific adjustments
        final_revenue = calculate_country_adjusted_revenue(
            adjusted_revenue, country, restaurant_type, city_group
        )
        
        # Add some randomness for realistic prediction
        try:
            np.random.seed(hash(f"{investment}{monthly_costs}{country}{city_group}{restaurant_type}") % 2**32)
            final_revenue += np.random.normal(0, final_revenue * 0.1)
        except Exception as e:
            logger.warning(f"⚠️ Error adding randomness to prediction: {e}")
        
        return max(final_revenue, 0)  # Ensure non-negative
        
    except Exception as e:
        logger.error(f"❌ Error in revenue prediction: {e}")
        # Fallback to simple calculation
        return max(investment * 0.3, 0)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page with error handling"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"❌ Error serving home page: {e}")
        return HTMLResponse(content="<h1>Restaurant Advisor MVP</h1><p>Service is running</p>")

@app.get("/pdf", response_class=HTMLResponse)
async def pdf_upload_page(request: Request):
    """PDF upload and analysis page"""
    try:
        return templates.TemplateResponse("pdf_upload.html", {"request": request})
    except Exception as e:
        logger.error(f"❌ Error rendering PDF upload page: {e}")
        return HTMLResponse(content="<h1>PDF Analysis</h1><p>PDF upload service is running</p>")

@app.post("/api/analyze")
async def analyze_restaurant(request: Request, data: Dict[str, Any]):
    """Analyze restaurant viability with comprehensive error handling"""
    
    try:
        # Rate limiting
        client_ip = get_client_ip(request)
        check_rate_limit(client_ip)
        
        # Validate and sanitize data
        restaurant_data = validate_and_sanitize_restaurant_data(data)
        
        # Basic analysis with additional validations
        investment = restaurant_data.investment
        monthly_costs = restaurant_data.monthly_costs
        
        # Business validations
        if investment <= 0:
            raise HTTPException(status_code=400, detail="Investment must be greater than 0")
        
        if monthly_costs <= 0:
            raise HTTPException(status_code=400, detail="Monthly costs must be greater than 0")
        
        # Revenue estimation using country-specific prediction
        revenue_estimate = simple_revenue_prediction(
            investment, 
            monthly_costs, 
            restaurant_data.country,
            restaurant_data.city_group, 
            restaurant_data.type
        )
        
        # Viability analysis
        annual_revenue = revenue_estimate
        annual_costs = monthly_costs * 12
        annual_profit = annual_revenue - annual_costs
        roi = (annual_profit / investment) * 100 if investment > 0 else 0
        
        viability_analysis = {
            "viability": "High" if annual_profit > 0 else "Low",
            "annual_revenue": annual_revenue,
            "annual_profit": annual_profit,
            "roi": roi,
            "analysis_date": datetime.now(timezone.utc).isoformat()
        }
        
        # Save to Supabase if configured (with comprehensive error handling)
        if supabase:
            try:
                supabase.table("restaurant_analyses").insert({
                    "restaurant_data": restaurant_data.dict(),
                    "revenue_estimate": revenue_estimate,
                    "viability_analysis": viability_analysis
                }).execute()
                logger.info(f"✅ Analysis saved to Supabase for IP: {client_ip}")
            except Exception as e:
                logger.error(f"❌ Error saving to Supabase: {e}")
                # Don't fail the application if Supabase fails
        
        # Activity log
        logger.info(f"✅ Analysis performed for {restaurant_data.city} by IP: {client_ip}")
        
        # Prepare response
        response = {
            "success": True,
            "revenue_estimate": revenue_estimate,
            "viability_analysis": viability_analysis
        }
        
        # Translate response if needed
        if restaurant_data.language != "en":
            try:
                from translation_service import translation_service
                response = translation_service.translate_analysis_response(
                    response, restaurant_data.language
                )
                logger.info(f"✅ Response translated to {restaurant_data.language}")
            except Exception as e:
                logger.warning(f"⚠️ Error translating response: {e}")
                # Continue with original response
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/ai_advice")
async def get_ai_advice(request: Request, data: Dict[str, Any]):
    """Get personalized AI advice with comprehensive error handling"""
    
    try:
        # Stricter rate limiting for AI
        client_ip = get_client_ip(request)
        check_rate_limit(client_ip, limit=5, window=60)  # 5 requests per minute
        
        # Validate data for AI advice
        if not openai.api_key or openai.api_key == "your_openai_api_key":
            return {
                "success": True,
                "advice": "To receive personalized AI advice, configure your OpenAI API key in the .env file"
            }
        
        # Validate input
        advice_request = AIAdviceRequest(**sanitize_input(data))
        
        # Create safe prompt
        safe_prompt = f"""
        Analyze this restaurant project professionally and constructively:
        
        City: {advice_request.city}
        Type: {advice_request.type}
        Investment: ${advice_request.investment:,.0f}
        Monthly costs: ${advice_request.monthly_costs:,.0f}
        
        Provide:
        1. 3 specific recommendations to improve viability
        2. Marketing strategies for the location
        3. Cost considerations and optimization
        4. Main risks to consider
        
        Respond in English in a professional and practical manner.
        """
        
        # OpenAI call with comprehensive error handling
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert restaurant consultant with 20 years of experience."},
                    {"role": "user", "content": safe_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            advice = response.choices[0].message.content
            
            # Sanitize AI response
            advice = re.sub(r'<[^>]*>', '', advice)  # Remove HTML tags
            advice = advice[:2000]  # Limit length
            
        except Exception as e:
            logger.error(f"❌ Error calling OpenAI: {e}")
            raise HTTPException(status_code=500, detail="Error generating AI advice")
        
        # Save to Supabase if configured
        if supabase:
            try:
                supabase.table("ai_advice").insert({
                    "restaurant_data": advice_request.dict(),
                    "advice": advice
                }).execute()
                logger.info(f"✅ AI advice saved for IP: {client_ip}")
            except Exception as e:
                logger.error(f"❌ Error saving advice to Supabase: {e}")
        
        # Activity log
        logger.info(f"✅ AI advice generated for {advice_request.city} by IP: {client_ip}")
        
        return {"success": True, "advice": advice}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in AI advice: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint with comprehensive status"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "openai": bool(openai.api_key and openai.api_key != "your_openai_api_key"),
                "supabase": bool(supabase),
                "python_version": sys.version,
                "environment": os.getenv("ENVIRONMENT", "production")
            }
        }
    except Exception as e:
        logger.error(f"❌ Error in health check: {e}")
        return {"status": "error", "message": str(e)}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP error handling with logging"""
    client_ip = get_client_ip(request)
    logger.warning(f"⚠️ HTTP Error {exc.status_code}: {exc.detail} from IP: {client_ip}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General error handling with comprehensive logging"""
    client_ip = get_client_ip(request)
    logger.error(f"❌ Unexpected error: {exc} from IP: {client_ip}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

# ============================================================================
# PDF UPLOAD AND ANALYSIS ENDPOINTS
# ============================================================================

@app.post("/api/pdf/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Carga un archivo PDF para análisis"""
    try:
        # Rate limiting
        client_ip = "pdf_upload"  # Simplified for PDF uploads
        if not check_rate_limit(client_ip, limit=5, window=60):
            raise HTTPException(status_code=429, detail="Too many PDF uploads")
        
        # Upload and process PDF
        result = await pdf_manager.upload_pdf(file)
        
        logger.info(f"✅ PDF uploaded: {result['filename']}")
        return {
            "success": True,
            "file_id": result["file_id"],
            "filename": result["filename"],
            "size": result["size"],
            "preview": result["text_content"][:200] + "..." if len(result["text_content"]) > 200 else result["text_content"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error uploading PDF: {e}")
        raise HTTPException(status_code=500, detail="Error uploading PDF")

@app.post("/api/pdf/{file_id}/analyze")
async def analyze_pdf(file_id: str):
    """Analiza un PDF específico usando sistema de caché inteligente"""
    try:
        # Rate limiting
        client_ip = "pdf_analysis"
        if not check_rate_limit(client_ip, limit=10, window=60):
            raise HTTPException(status_code=429, detail="Too many analysis requests")
        
        # Buscar archivo
        pdf_files = list(pdf_manager.upload_dir.glob(f"{file_id}_*"))
        if not pdf_files:
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        file_path = pdf_files[0]
        filename = file_path.name
        
        # Analizar con sistema de caché
        analysis_result = pdf_analyzer.analyze_pdf_with_cache(str(file_path), file_id, filename)
        
        if not analysis_result["success"]:
            raise HTTPException(status_code=500, detail=f"Error analyzing PDF: {analysis_result.get('error', 'Unknown error')}")
        
        # Extraer datos de restaurantes (siempre procesar para datos específicos)
        text_content = pdf_analyzer._extract_text_from_file(str(file_path))
        restaurant_data = pdf_analyzer.extract_restaurant_data(text_content)
        
        # Generar insights
        insights = pdf_analyzer.generate_insights(
            analysis_result.get("analysis", {}),
            restaurant_data.get("data", {})
        )
        
        # Calcular costos
        cost_estimate = pdf_analyzer.get_cost_estimate(len(text_content))
        
        # Información de caché
        cache_info = {
            "from_cache": analysis_result.get("from_cache", False),
            "cache_hit": analysis_result.get("cache_hit", False),
            "processing_time": analysis_result.get("processing_time", 0)
        }
        
        logger.info(f"✅ PDF analyzed: {file_id}, from_cache: {cache_info['from_cache']}, tokens: {analysis_result.get('tokens_used', 0)}")
        
        return {
            "success": True,
            "file_id": file_id,
            "analysis": analysis_result.get("analysis", {}),
            "restaurant_data": restaurant_data.get("data", {}),
            "insights": insights.get("insights", {}),
            "cost_estimate": cost_estimate,
            "tokens_used": analysis_result.get("tokens_used", 0) + restaurant_data.get("tokens_used", 0) + insights.get("tokens_used", 0),
            "cache_info": cache_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error analyzing PDF: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing PDF")

@app.post("/api/analyze_with_pdf")
async def analyze_restaurant_with_pdf(request: Request, data: Dict[str, Any]):
    """Analiza restaurante incluyendo datos de PDFs"""
    try:
        # Rate limiting
        client_ip = get_client_ip(request)
        if not check_rate_limit(client_ip):
            raise HTTPException(status_code=429, detail="Too many requests")
        
        # Validar datos del restaurante
        restaurant_data = validate_and_sanitize_restaurant_data(data)
        
        # Obtener datos de PDF si están disponibles
        pdf_data = None
        if "pdf_file_id" in data:
            pdf_files = list(pdf_manager.upload_dir.glob(f"{data['pdf_file_id']}_*"))
            if pdf_files:
                file_path = pdf_files[0]
                text_content = pdf_manager._extract_text(file_path)
                pdf_analysis = pdf_analyzer.analyze_pdf_content(text_content)
                pdf_data = {
                    "analysis": pdf_analysis.get("analysis", {}),
                    "text_content": text_content
                }
        
        # Análisis de viabilidad con PDF
        viability_result = prompt_engine.analyze_viability(restaurant_data.dict(), pdf_data)
        
        # Predicción de revenue con PDF
        revenue_result = prompt_engine.predict_revenue(restaurant_data.dict(), pdf_data)
        
        # Análisis de competencia con PDF
        competition_result = prompt_engine.analyze_competition(restaurant_data.city, pdf_data)
        
        # Recomendaciones estratégicas con PDF
        recommendations_result = prompt_engine.generate_strategic_recommendations(restaurant_data.dict(), pdf_data)
        
        # Calcular revenue básico
        basic_revenue = simple_revenue_prediction(
            restaurant_data.investment,
            restaurant_data.monthly_costs,
            restaurant_data.city_group,
            restaurant_data.type
        )
        
        # Combinar resultados
        total_tokens = (
            viability_result.get("tokens_used", 0) +
            revenue_result.get("tokens_used", 0) +
            competition_result.get("tokens_used", 0) +
            recommendations_result.get("tokens_used", 0)
        )
        
        logger.info(f"✅ Restaurant analyzed with PDF: {restaurant_data.city}, tokens used: {total_tokens}")
        
        return {
            "success": True,
            "restaurant_data": restaurant_data.dict(),
            "viability_analysis": viability_result.get("analysis", {}),
            "revenue_prediction": revenue_result.get("prediction", {}),
            "competition_analysis": competition_result.get("analysis", {}),
            "strategic_recommendations": recommendations_result.get("recommendations", {}),
            "basic_revenue": basic_revenue,
            "pdf_integrated": pdf_data is not None,
            "total_tokens_used": total_tokens,
            "cost_estimate": prompt_engine.get_cost_summary()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in restaurant analysis with PDF: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing restaurant")

@app.post("/api/analyze_with_ml")
async def analyze_restaurant_with_ml(request: Request, data: Dict[str, Any]):
    """Analiza restaurante usando el modelo ML original de Kaggle"""
    try:
        # Rate limiting
        client_ip = get_client_ip(request)
        if not check_rate_limit(client_ip):
            raise HTTPException(status_code=429, detail="Too many requests")
        
        # Validar datos del restaurante
        restaurant_data = validate_and_sanitize_restaurant_data(data)
        
        # Obtener datos de PDF si están disponibles
        pdf_data = None
        if "pdf_file_id" in data:
            pdf_files = list(pdf_manager.upload_dir.glob(f"{data['pdf_file_id']}_*"))
            if pdf_files:
                file_path = pdf_files[0]
                text_content = pdf_manager._extract_text(file_path)
                pdf_analysis = pdf_analyzer.analyze_pdf_content(text_content)
                pdf_data = {
                    "analysis": pdf_analysis.get("analysis", {}),
                    "text_content": text_content
                }
        
        # Predicción usando modelo ML original
        ml_prediction = ml_integration.predict_revenue_ml(restaurant_data.dict(), pdf_data)
        
        # Análisis de viabilidad con PDF
        viability_result = prompt_engine.analyze_viability(restaurant_data.dict(), pdf_data)
        
        # Análisis de competencia con PDF
        competition_result = prompt_engine.analyze_competition(restaurant_data.city, pdf_data)
        
        # Recomendaciones estratégicas con PDF
        recommendations_result = prompt_engine.generate_strategic_recommendations(restaurant_data.dict(), pdf_data)
        
        # Calcular métricas financieras básicas
        annual_revenue = ml_prediction.get("revenue_prediction", 0)
        annual_costs = restaurant_data.monthly_costs * 12
        annual_profit = annual_revenue - annual_costs
        roi = (annual_profit / restaurant_data.investment) * 100 if restaurant_data.investment > 0 else 0
        
        # Calcular proyecciones a 2, 5 y 10 años
        projection = investment_projection.calculate_projection(
            initial_investment=restaurant_data.investment,
            initial_revenue=annual_revenue,
            initial_monthly_costs=restaurant_data.monthly_costs,
            years=10
        )
        
        key_metrics = investment_projection.get_key_metrics(projection)
        
        viability_analysis = {
            "viability": "High" if annual_profit > 0 else "Low",
            "annual_revenue": annual_revenue,
            "annual_profit": annual_profit,
            "roi": roi,
            "confidence": ml_prediction.get("confidence", 0.5),
            "analysis_date": datetime.now(timezone.utc).isoformat(),
            "projections": key_metrics,
            "full_projection": projection
        }
        
        # Combinar resultados
        total_tokens = (
            viability_result.get("tokens_used", 0) +
            competition_result.get("tokens_used", 0) +
            recommendations_result.get("tokens_used", 0)
        )
        
        logger.info(f"✅ ML analysis completed for {restaurant_data.city}, confidence: {ml_prediction.get('confidence', 0)}")
        
        return {
            "success": True,
            "restaurant_data": restaurant_data.dict(),
            "ml_prediction": ml_prediction,
            "viability_analysis": viability_analysis,
            "competition_analysis": competition_result.get("analysis", {}),
            "strategic_recommendations": recommendations_result.get("recommendations", {}),
            "pdf_integrated": pdf_data is not None,
            "total_tokens_used": total_tokens,
            "model_info": ml_integration.get_model_info(),
            "cost_estimate": prompt_engine.get_cost_summary()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in ML analysis: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing restaurant with ML")

@app.get("/api/pdf/cost-info")
async def get_pdf_cost_info():
    """Obtiene información de costos para análisis de PDFs"""
    try:
        return {
            "success": True,
            "pdf_analyzer_cost": pdf_analyzer.get_cost_estimate(1000),
            "prompt_engine_cost": prompt_engine.get_cost_summary(),
            "optimization_tips": [
                "Usando gpt-3.5-turbo (más económico)",
                "Tokens limitados por request",
                "Análisis optimizado para economía",
                "Respuestas en JSON para eficiencia"
            ]
        }
    except Exception as e:
        logger.error(f"❌ Error getting cost info: {e}")
        raise HTTPException(status_code=500, detail="Error getting cost information")

@app.get("/api/ml/model-info")
async def get_ml_model_info():
    """Obtiene información sobre el modelo ML de Kaggle"""
    try:
        model_info = ml_integration.get_model_info()
        return {
            "success": True,
            "model_info": model_info,
            "description": "Modelo ML original entrenado en Kaggle para predicción de revenue de restaurantes",
            "features": [
                "Predicción basada en Random Forest",
                "Integración con datos de PDFs",
                "Ajustes automáticos por competencia",
                "Cálculo de confianza",
                "Fallback a predicción simple"
            ]
        }
    except Exception as e:
        logger.error(f"❌ Error getting ML model info: {e}")
        raise HTTPException(status_code=500, detail="Error getting ML model information")

@app.get("/api/pdf/cache-stats")
async def get_pdf_cache_stats():
    """Obtiene estadísticas del sistema de caché de PDFs"""
    try:
        from pdf_cache_manager import pdf_cache
        stats = pdf_cache.get_analysis_stats()
        
        return {
            "success": True,
            "cache_stats": stats,
            "description": "Sistema de caché inteligente para PDFs",
            "benefits": [
                "Reduce costos de OpenAI",
                "Mejora tiempo de respuesta",
                "Evita re-procesamiento de PDFs",
                "Cache en memoria y base de datos",
                "Validación automática de análisis"
            ]
        }
    except Exception as e:
        logger.error(f"❌ Error getting PDF cache stats: {e}")
        raise HTTPException(status_code=500, detail="Error getting cache stats")

@app.get("/api/countries")
async def get_countries():
    """Obtiene lista de países disponibles"""
    try:
        from country_data import COUNTRY_DATA
        
        countries = []
        for country_code, country_data in COUNTRY_DATA.items():
            countries.append({
                "code": country_code,
                "name": country_data["name"],
                "currency": country_data["currency"],
                "major_cities": country_data["major_cities"]
            })
        
        return {
            "success": True,
            "countries": countries,
            "description": "Países disponibles para análisis de restaurantes"
        }
    except Exception as e:
        logger.error(f"❌ Error getting countries: {e}")
        raise HTTPException(status_code=500, detail="Error getting countries")

@app.get("/api/countries/{country}/cities")
async def get_cities_by_country(country: str):
    """Obtiene ciudades principales por país"""
    try:
        from country_data import get_cities_by_country, get_country_data
        
        cities = get_cities_by_country(country)
        country_data = get_country_data(country)
        
        if not cities:
            raise HTTPException(status_code=404, detail="Country not found")
        
        return {
            "success": True,
            "country": country,
            "country_name": country_data.get("name", country),
            "cities": cities,
            "total_cities": len(cities)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting cities for {country}: {e}")
        raise HTTPException(status_code=500, detail="Error getting cities")

@app.get("/api/countries/{country}/insights")
async def get_country_insights(country: str):
    """Obtiene insights económicos específicos por país"""
    try:
        from country_data import get_country_economic_insights
        
        insights = get_country_economic_insights(country)
        
        if not insights.get("country_name"):
            raise HTTPException(status_code=404, detail="Country not found")
        
        return {
            "success": True,
            "country": country,
            "insights": insights
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting insights for {country}: {e}")
        raise HTTPException(status_code=500, detail="Error getting country insights")

@app.get("/api/languages")
async def get_languages():
    """Obtiene información sobre idiomas disponibles"""
    try:
        from translation_service import translation_service
        
        language_info = translation_service.get_language_info()
        
        return {
            "success": True,
            "languages": language_info,
            "description": "Idiomas disponibles para traducción automática"
        }
    except Exception as e:
        logger.error(f"❌ Error getting languages: {e}")
        raise HTTPException(status_code=500, detail="Error getting languages")

if __name__ == "__main__":
    try:
        import uvicorn
        logger.info("🚀 Starting Restaurant Advisor MVP with ML + PDF integration...")
        logger.info("📊 ML Model Status:")
        model_info = ml_integration.get_model_info()
        if model_info.get("models_loaded", {}).get("full_model"):
            logger.info("✅ Full ML model loaded successfully")
        if model_info.get("models_loaded", {}).get("simple_model"):
            logger.info("✅ Simple ML model loaded successfully")
        logger.info("🎯 Ready for production with ML-powered predictions!")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"❌ Error starting application: {e}")
        sys.exit(1) 